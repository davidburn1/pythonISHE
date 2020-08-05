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
		positions = np.arange(start, (stop+0.1), step)			# 0.1 extra so stop is included
	else:
		positions = np.arange(start, (stop-0.1), step)			# 0.1 extra so stop is included		
			
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
		

		
		
		
		
		
		
		
		
		
		
		
		
		

class vnafmrClass():
	def __init__(self, vna, mag, path):
		self.vna = vna
		self.mag = mag
		self.path = path
		
		self.f = None
		self.freqPts = 0
		
	def startNewScan(self):
		pass

	def measureRef(self):
		#self.mag.setField(500)
		self.vna.doSweep()
		#freq = self.vna.getFrequency()
		#self.freqPts = len(freq)
		
		self.vna.inst.write("CALCULATE1:PARAMETER:SELECT 'Trc1'")
		#self.vna.inst.write("CORR:LOSS:AUTO ONCE")					# auto length and loss correction
		self.vna.inst.write("CORR:EDEL:AUTO ONCE")
		
		self.f.attrs['electrical_length'] = self.vna.inst.query("CORRection:EDELay1:ELENgth?")
		print "the electrical length is " + self.f.attrs['electrical_length']

		#self.vna.inst.write("DISP:WIND1:TRAC1:Y:BOTT 0; TOP 20")	# set the screen scale 
		#self.vna.inst.write("DISP:WIND1:TRAC1:Y:RLEV 0")			# reference value
		#self.vna.inst.write("DISP:WIND1:TRAC1:Y:RPOS 0")			# reference position
		self.vna.inst.write("DISPlay:WINDow1:TRACe1:Y:SCALe:AUTO ONCE") 			# autoscale
		
		#self.vna.inst.write("CALCULATE1:PARAMETER:SELECT 'Trc2'")
		#self.vna.inst.write("CORR:LOSS:AUTO ONCE")
		
		#self.vna.inst.write("DISP:WIND2:TRAC1:Y:BOTT 0; TOP 20")	# set the screen scale 
		#self.vna.inst.write("DISP:WIND2:TRAC1:Y:RLEV 0")			# reference value
		#self.vna.inst.write("DISP:WIND2:TRAC1:Y:RPOS 0")			# reference position
		self.vna.inst.write("DISPlay:WINDow2:TRACe1:Y:SCALe:AUTO ONCE")
		
		#s12r, s21r, s11r, s22r = self.vna.getData()
			

		#i = np.shape(self.f['s12r'])[0]
		#self.f['s12r'].resize((i+1, self.freqPts))
		#self.f['s21r'].resize((i+1, self.freqPts))
		#self.f['s11r'].resize((i+1, self.freqPts))
		#self.f['s22r'].resize((i+1, self.freqPts))
			
		#self.f['s12r'][i,:] = s12r
		#self.f['s21r'][i,:] = s21r
		#self.f['s11r'][i,:] = s11r
		#self.f['s22r'][i,:] = s22r
		
	def fieldScan(self, start, stop, step):
		self.scanStart()
		self.measureRef()
		if (stop > start) :
			fields = np.arange(start, (stop+0.1), step)			# 0.1 extra so stop is included
		else:
			fields = np.arange(start, (stop-0.1), step)			# 0.1 extra so stop is included		
		self.f.create_dataset('field', (0,), chunks=(1,), maxshape=(None,))
		
		self.f.attrs['power'] = self.vna.power 
		self.f.attrs['bandwidth'] = self.vna.bandwidth
		self.f.attrs['averages'] = self.vna.averages 
		
		self.f.attrs['theta'] = self.mag.theta 
		self.f.attrs['phi'] = self.mag.phi 
		
		for field in fields:
			self.mag.setField(field)			
			time.sleep(2)
			
			i = np.shape(self.f['field'])[0]
			self.scanStep(i)
			self.f['field'].resize((i+1,))
			self.f['field'][i] = field
			self.f.flush()
			
		self.f.close()
		
		
	def fieldScanWithReference(self, start, stop, step, refField):
		self.scanStart()
		#self.measureRef()
		if (stop > start) :
			fields = np.arange(start, (stop+0.1), step)			# 0.1 extra so stop is included
		else:
			fields = np.arange(start, (stop-0.1), step)			# 0.1 extra so stop is included		
		self.f.create_dataset('field', (0,), chunks=(1,), maxshape=(None,))
		
		self.f.attrs['power'] = self.vna.power 
		self.f.attrs['bandwidth'] = self.vna.bandwidth
		self.f.attrs['averages'] = self.vna.averages 
		
		self.f.attrs['theta'] = self.mag.theta 
		self.f.attrs['phi'] = self.mag.phi 
		
		for field in fields:
			i = np.shape(self.f['field'])[0]
			
			self.mag.setField(refField)			
			time.sleep(2)
			self.refStep(i)			
			
			self.mag.setField(field)			
			time.sleep(2)
			self.scanStep(i)
			
			self.f['field'].resize((i+1,))
			self.f['field'][i] = field
			self.f.flush()
			
		self.f.close()
		
	def dummyScan(self,steps):
		self.scanStart()
		dummy = np.arange(1, steps, 1)
		self.f.create_dataset('dummy', (0,), chunks=(1,), maxshape=(None,))
		
		for d in dummy:
			print "dummy: %4d " % d
			i = np.shape(self.f['dummy'])[0]
			self.f['dummy'].resize((i+1,))
			self.scanStep(i)
			self.f.flush()
	

	def tempScan(self, start, stop, rate):
		from rasorTemperature import rasorTemperature
		rasorTemp = rasorTemperature()

		rasorTemp.waitForStableTemp(start)	

		self.scanStart()
		self.f.create_dataset('waveguide_temp', (0,), chunks=(1,), maxshape=(None,))
		self.f.create_dataset('cryo_temp', (0,), chunks=(1,), maxshape=(None,))


		
		rasorTemp.startSweep(start, stop, rate)
			
		while rasorTemp.isSweepRunning():

			i = np.shape(self.f['waveguide_temp'])[0]
			self.scanStep(i)
			waveguide, cryo = rasorTemp.getTemp()
			self.f['waveguide_temp'].resize((i+1,))
			self.f['cryo_temp'].resize((i+1,))
			self.f['waveguide_temp'][i] = waveguide
			self.f['cryo_temp'][i] = cryo
			self.f.flush()

			print "temp: %0.2f mT" % waveguide
		rasorTemp.setTemp(stop)
		self.f.close()
			
	
	
	def scanStart(self):
		pass

		

		

		
		
	def scanStep(self, i):
		pass
		
	def refStep(self, i):
		self.vna.doSweep()
		s12, s21 = self.vna.getData()
		grp = self.f
		freqPts = self.freqPts
		grp['s12r'].resize((i+1, freqPts))
		grp['s21r'].resize((i+1, freqPts))

		grp['s12r'][i,:] = s12
		grp['s21r'][i,:] = s21
		



		
	


		
		
		



