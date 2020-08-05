"""

"""


import visa
import numpy as np
import time

class RSSMF100A():
	def __init__(self, host):
		rm = visa.ResourceManager()
		self.inst = rm.open_resource(host)
		print(self.inst.query("*IDN?"))

		self.power = 0 #dBm
		self.freq = 0

	def write(self,data):
		self.inst.write(data)


		
	def setup(self):
		#self.inst.write("*RST")
		
		""" wait until all functions complete before proceeding """
		# self.inst.write("*OPC") 
		# while int(self.inst.query("*ESR?")) != 1:
		# 	print "waiting after setup"
		# 	time.sleep(0.1)
	
			
	def setFrequency(self, freq):
		self.freq = freq
		self.inst.write("SOUR1:FREQ %f GHz" % self.freq)
	
	def setPower(self, power):
		if (power >= 23):
			print "23 dBm is the maximum input for the NRP-Z31 power meter -> not set"
			return

		self.power = power
		self.inst.write("SOUR:POW %2d" % power)
		


	def readPower(self):
		return float(self.inst.query("READ1?"))

		#SENS:POW:APER:TIM 23ms


		#SENSe:UNIT[:POWer].

# 		The power analysis measurement is started with the
# SENSe[:POWer]:SWEep:INITiate command and the measurement result retrieved
# with the TRACe[:POWer]:SWEep: commands.
# The four sensors are distinguished by means of the suffix at the second key word
# SENSe.
		

	def rfOn(self):
		self.inst.write("OUTP:ALL ON")

	def rfOff(self):
		self.inst.write("OUTP:ALL OFF")

	def returnToLocal(self):
		self.inst.write("&GTL")

	
#print a.inst.query("CALCulate1:PARameter:CAT?")




class powerMeterScannable():
	def __init__(self, device):
		self.device = device
		self.name = "power_meter"

	def collectData(self):
		pass

	def waitWhileBusy(self):
		pass

	def readout(self):
		return float(self.device.inst.query("READ1?"))


class frequencyScannable():
	def __init__(self, device):
		self.device = device
		self.name = "frequency"

	def moveTo(self, newPosition):
		self.device.setFrequency(newPosition)




