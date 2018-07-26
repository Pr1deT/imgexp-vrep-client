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

class vrepsim:
	def __init__(self):
		# -1: not connected
		self.clientID = -1

	def is_connected(self):
		if (self.clientID != -1):
			return True
		else:
			return False

	def connect(self):
		vrep.simxFinish(-1) # just in case, close all opened connections
		self.clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5) # Connect to V-REP

		if (self.clientID != -1):
			print ('Connected to remote API server')
		else:
			print ('Failed connecting to remote API server')

		#return True

	def disconnect(self):
		if (self.is_connected()==False):
			print ('Error: no connection has been established')
			return False
		
		# Before closing the connection to V-REP, make sure that the last command sent out had 
		# time to arrive. You can guarantee this with (for example):
		vrep.simxGetPingTime(self.clientID)

		# Now close the connection to V-REP:
		vrep.simxFinish(self.clientID)
		print ('Disconnected from remote API server')

		return True

	def reset(self):
		if (self.is_connected()==False):
			print ('Error: no connection has been established')
			self.connect()
			# get omega handle
			res, self.omega = vrep.simxGetObjectHandle(self.clientID,'Omega_test',vrep.simx_opmode_blocking)
			if res==vrep.simx_return_ok:
				print ("Get Omega handle") # display the reply from V-REP (in this case, the handle of the created dummy)
			else:
				print ('Remote function call failed: Get Omega handle')
				return False
			# get omega position
			res, self.init_pos = vrep.simxGetObjectPosition(self.clientID,self.omega,-1,vrep.simx_opmode_blocking)
			if res==vrep.simx_return_ok:
				print ("Get Omega position") # display the reply from V-REP (in this case, the handle of the created dummy)
			else:
				print ('Remote function call failed: Get Omega position')

		else:
			#set omega to initial position
			res = vrep.simxSetObjectPosition(self.clientID,self.omega,-1,self.init_pos,vrep.simx_opmode_blocking)
			if res==vrep.simx_return_ok:
				print ("Reset Omega position") # display the reply from V-REP (in this case, the handle of the created dummy)
				return True
			else:
				print ('Remote function call failed: Reset Omega position')
				return False

		self.start_state = ['wall_top',self.init_pos[0],self.init_pos[1]]
		self.end_state = self.start_state

		return True
	
	def get_obj_size(self, name):
		# get handle
		"""
		res, red_h = vrep.simxGetObjectHandle(self.clientID,name,vrep.simx_opmode_blocking)
		if res==vrep.simx_return_ok:
			print ("Get object handle") # display the reply from V-REP (in this case, the handle of the created dummy)
		else:
			print ('Remote function call failed: Get object handle')
			return False
		res,x = vrep.simxGetObjectFloatParameter(self.clientID,red_h,)
		"""
		# size of red blood cell
		width = 60.35
		return width

	# build environment related functions ----------------------------------------------------
	def build_test_image(self,cell_list):
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

	# take one step of action -------------------------------------------------------------------
	def step(self,action,gama=0,pctg=0):
		if (self.is_connected()==False):
			print ('Error: no connection has been established')
			return False

		self.start_state = self.end_state
		if (action=='go_straight'):
			# rotate to right orientation
			self._send_command('rotate',gama,pctg)
			self._send_command('go_straight',0,0)
			while (not self.is_hit()):
				pass
		elif (action=='path'):
			self._send_command(action,gama,pctg)
			while (not self.path_stop()):
				pass

		hit_name = self.get_hit_object_name()
		end_pos = []
		res, end_pos = vrep.simxGetObjectPosition(self.clientID,self.omega,-1,vrep.simx_opmode_blocking)
		if res==vrep.simx_return_ok:
			print ("Get Omega position") # display the reply from V-REP (in this case, the handle of the created dummy)
		else:
			print ('Remote function call failed: Get omega position')

		self.end_state = [hit_name,end_pos[0],end_pos[1]]

		return self.start_state,self.end_state

	def is_hit(self):
		hit = 0
		res, hit = vrep.simxGetIntegerSignal(self.clientID,'hit',vrep.simx_opmode_blocking)
		if res==vrep.simx_return_ok:
			pass
			#print ("hit ", hit) # display the reply from V-REP (in this case, the handle of the created dummy)
		else:
			print ('Remote function call failed: is_hit')

		if (hit==1):
			vrep.simxSetIntegerSignal(self.clientID,'hit',0,vrep.simx_opmode_blocking)

		return hit

	def path_stop(self):
		hit = 0
		res, hit = vrep.simxGetIntegerSignal(self.clientID,'path_stop',vrep.simx_opmode_blocking)
		if res==vrep.simx_return_ok:
			print ("path stop  ", hit) # display the reply from V-REP (in this case, the handle of the created dummy)
		else:
			print ('Remote function call failed: path_stop')

		return hit

	def get_possible_action_list(self):
		action_list = []
		gama_range = []
		# get current status through hit object
		hit_name = self.get_hit_object_name()
		if (hit_name == ''):
			action_list = ['go_straight']
			gama_range = range(0,90)
		else:
			str_list = hit_name.split('_')
			if (str_list[0]=='wall'):
				action_list = ['go_straight']
			elif (str_list[0]=='cell'):
				action_list = ['go_straight','path']

			gama_range = self._get_gama_range(str_list[1])

		return action_list, gama_range

	def _get_gama_range(self, side):
		gama_range = []
		if (side=='top'):
			gama_range = range(0,90)+range(270,360)
		elif(side=='bottom'):
			gama_range = range(90,270)
		elif(side=='left'):
			gama_range = range(0,180)
		elif(side=='right'):
			gama_range = range(180,360)
		else:
			res, angle = vrep.simxGetIntegerSignal(self.clientID,'gama',vrep.simx_opmode_blocking)
			if res==vrep.simx_return_ok:
				pass
				#print ("gama ", angle) # display the reply from V-REP (in this case, the handle of the created dummy)
			else:
				print ('Remote function call failed: get gama')
			gama_range = range(angle-30, angle+30)

		return gama_range


	def get_hit_object_name(self):
		hit_name = ''
		res, hit_name = vrep.simxGetStringSignal(self.clientID,'hit_name',vrep.simx_opmode_blocking)
		if res==vrep.simx_return_ok:
			pass
			#print ("hit ", hit_name) # display the reply from V-REP (in this case, the handle of the created dummy)
		else:
			print ('Remote function call failed: take action')

		return hit_name

	def get_state(self):
		if (self._is_connected()==False):
			print ('Error: no connection has been established')
			return False

	def _send_command(self,action,gama,pctg):
		emptyBuff = bytearray()

		if (gama<0):
			gama += 360

		res,retInts,retFloats,retStrings,retBuffer=vrep.simxCallScriptFunction(self.clientID,'Omega_test',vrep.sim_scripttype_childscript,'get_command',[gama,pctg],[],[action],emptyBuff,vrep.simx_opmode_blocking)
		if res==vrep.simx_return_ok:
			print ("action: ", action) # display the reply from V-REP (in this case, the handle of the created dummy)
			return True
		else:
			print ('Remote function call failed: take action', action)
			return False


if __name__ == '__main__':
	sim = vrepsim()
	sim.connect()
	action = 'rotate'
	gama = 45
	sim.step(action,gama)
	action = 'go_straight'
	sim.step(action)
	while (not sim.is_hit()):
		pass
	action_list, gama_range = sim.get_possible_action_list()
	print(action_list)
	
	action = 'path'
	pctg = 80
	sim.step(action,0,pctg)
	while(not sim.path_stop()):
		pass
	action_list, gama_range = sim.get_possible_action_list()
	print(action_list)
	action = 'rotate'
	gama = gama_range[20]
	sim.step(action,gama)
	action = 'go_straight'
	sim.step(action)


