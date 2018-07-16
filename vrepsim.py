"""
vrep simulation
"""

try:
	import vrep
except:
	print ('--------------------------------------------------------------')
	print ('"vrep.py" could not be imported. This means very probably that')
	print ('either "vrep.py" or the remoteApi library could not be found.')
	print ('Make sure both are in the same folder as this file,')
	print ('or appropriately adjust the file "vrep.py"')
	print ('--------------------------------------------------------------')
	print ('')

class vrepsim(object):
	def __init__(self):
		# -1: not connected
		self.clientID = -1

	def _is_connected(self):
		if (self.clientID != -1):
			return True
		else:
			return False

	def connect():
		vrep.simxFinish(-1) # just in case, close all opened connections
		self.clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5) # Connect to V-REP

		if (self.clientID != -1):
			print ('Connected to remote API server')
		else:
			print ('Failed connecting to remote API server')

		return self.clientID

	def disconnect():
		if (self._is_connected()==False):
			print ('Error: no connection has been established')
			return False
		
		# Before closing the connection to V-REP, make sure that the last command sent out had 
		# time to arrive. You can guarantee this with (for example):
		vrep.simxGetPingTime(self.clientID)

		# Now close the connection to V-REP:
		vrep.simxFinish(self.clientID)
		print ('Disconnected from remote API server')

		return True

	# build environment related functions ----------------------------------------------------
	def build_test_image(cell_list):
		for i in range(len(cell_list)):
			self.add_to_env(cell_list[i])
		


	def _add_to_env(self, cell):
		# cell[0]: type of cell. 1: red. 2: white. 
		if (cell[0]==1):
			cell_type = 'red'
		elif (cell[0]==2):
			cell_type = 'white'

		# get object handle to copy
		res, obj_h = vrep.simxGetObjectHandle(self.clientID,cell_type,vrep.simx_opmode_blocking)
		if res==vrep.simx_return_ok:
			print ("Get Red cell handle") # display the reply from V-REP (in this case, the handle of the created dummy)
			return True
		else:
			print ('Remote function call failed: Get red cell handle')
			return False
		res = vrep.simxCopyPasteObjects(self.clientID,obj_h,vrep.simx_opmode_blocking)


	def step(action):
		if (self._is_connected()==False):
			print ('Error: no connection has been established')
			return False

		res,retInts,retFloats,retStrings,retBuffer=vrep.simxCallScriptFunction(self.clientID,'Omega_test',vrep.sim_scripttype_childscript,'moveOmega_function',[action],[],[],emptyBuff,vrep.simx_opmode_blocking)
		if res==vrep.simx_return_ok:
			print ("action: ", action) # display the reply from V-REP (in this case, the handle of the created dummy)
			return True
		else:
			print ('Remote function call failed: take action')
			return False

	def get_state():
		if (self._is_connected()==False):
			print ('Error: no connection has been established')
			return False




if __name__ == '__main__':
	sim = vrepsim()
	sim.connect()
