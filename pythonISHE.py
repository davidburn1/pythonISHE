import numpy as np
import matplotlib.pyplot as plt
import time
import h5py
import os


from pomsMagnets import vmag as vmagClass
from RSSMF100A import RSSMF100A, powerMeterScannable, frequencyScannable
from ZurichMFLI import ZurichMFLI 









""" field configuration """
vmag = vmagClass("172.23.240.102", 4042) 				# POMS raspberry in the lab
vmag.setAngle(0,0)
vmag.setField(0)

			

""" RF generator configuration """
rfGen = RSSMF100A("TCPIP::172.23.240.196::INSTR")
#rfGen.write("*RST")

		
# # setup modulation input
rfGen.write("AM1:SOUR EXT1") # select modulation source 
rfGen.write("AM1:DEPT 100PCT") #100% amplitude modulation
rfGen.write("AM1:STAT ON") # activate amplitude modulation

rfGen.write("SOUR:POW:ALC ON") # Turn on automatic level control

rfGen.write("SENS:UNIT DBM") # set dBm units
rfGen.inst.write("SENS1:POW:DISP:PERM:STAT ON")	#perminantly show measured power on screen



rfGen.setPower(-20)




""" LIA configuration """
lia = ZurichMFLI("172.23.240.161", 8004) 
lia.name = "vISHE"	
lia.daq.setInt('/dev4206/demods/0/adcselect', 0) 	# set voltage input

# set reference
lia.daq.setInt('/dev4206/extrefs/0/enable', 0)		# use internal reference
lia.daq.setInt('/dev4206/sigouts/0/enables/1', 1)	# enable the output of the internal reference
lia.daq.setDouble('/dev4206/sigouts/0/amplitudes/1', 1.0)	# 1V for the output reference
lia.daq.setDouble('/dev4206/oscs/0/freq', 3333)		#set reference frequency


# set adc range
lia.daq.setDouble('/dev4206/sigins/0/range', 0.01) # set input amplifier range to 10 mA

lia.daq.setDouble('/dev4206/demods/0/timeconstant', 0.811410938)





""" scannable configuration """
readPower = powerMeterScannable(rfGen)
frequency = frequencyScannable(rfGen)




directory = ""


def setDirectory(newDirectory):
	global directory
	directory = newDirectory
	if not os.path.exists(directory):
		print "Directory doesn't exist -> creating %s" % directory
		os.makedirs(directory)

def dummyScan():
    global directory
    print directory
    






def scan(axis, start, stop, step, detectors):
	global directory
    
	if (stop > start) :
		positions = np.arange(start, (stop+0.00001), step)			# 0.1 extra so stop is included
	else:
		positions = np.arange(start, (stop-0.00001), step)			# 0.1 extra so stop is included		
			
	# increment the scan number counter
	count = np.loadtxt("./scanCounter.dat", dtype="d")
	count = count + 1
	np.savetxt("./scanCounter.dat", [count], fmt="%06d")
	
	# open new scan file
	print "Starting scan %s #%06d" % (directory, count)
	f = h5py.File(directory + "/poms-%06d.hdf5" % count, "w", libver='latest')
	f.swmr_mode = True

	# metadata
	# f.attrs['power'] = rfGen.power 
	# f.attrs['frequency'] = rfGen.frequency
	# f.attrs['theta'] = vmag.theta 
	# f.attrs['phi'] = vmag.phi 


	grp = f
	# setup datasets
	grp.create_dataset(axis.name, data=positions)
	for d in detectors:
		grp.create_dataset(d.name, (len(positions),), dtype=np.float)


	

	# do the scan
	for i, position in enumerate(positions):
		print "%s: %f" % (axis.name, position)

		axis.moveTo(position)	
		#wait while moving	

		# collect data
		for d in detectors:
			d.collectData()

		# wait while busy
		for d in detectors:
			d.waitWhileBusy()

		# readout	
		for d in detectors:
			grp[d.name][i] = d.readout()

		f.flush()

	f.close()
		

		
		
		
		
		
		
		
		
		
		
		



