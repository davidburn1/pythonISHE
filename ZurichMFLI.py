"""

"""

import numpy as np
import time

import zhinst.ziPython



class ZurichMFLI():
	def __init__(self, host, port):
		# Open connection to ziServer
		self.daq = zhinst.ziPython.ziDAQServer(host, port, 6)

		self.daq.setInt('/dev4206/demods/0/enable', 1) 		# Enable the demodulator output
		self.daq.setInt('/dev4206/demods/0/rate', 100) 		# set transfer rate 100 S/s

		self.daq.subscribe('/dev4206/demods/0/sample')

		self.name = "lia"
		self.isBusy = False

	def write(self,data):
		self.inst.write(data)


	def collectData(self):
		self.isBusy = True
		time.sleep(1)
		self.isBusy = False

	def waitWhileBusy(self):
		while self.isBusy:
			pass

	def readout(self):
		data_d = self.daq.poll(0.020, 10, 0, True) # poll demodulator outputs 
		#print data_d['/dev4206/demods/0/sample'].keys()
		x = data_d['/dev4206/demods/0/sample']['x'][:-100].mean() # mean of demodulator output in the last 100 samples (1 s)
		y = data_d['/dev4206/demods/0/sample']['y'][:-100].mean()
		return x
		#return {'x':x, 'y':y}


	
