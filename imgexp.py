# Make sure to have the server side running in V-REP: 
# in a child script of a V-REP scene, add following command
# to be executed just once, at simulation start:
#
# simRemoteApi.start(19999)
#
# then start simulation, and run this program.
#
# IMPORTANT: for each successful call to simxStart, there
# should be a corresponding call to simxFinish at the end!

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

import time
import numpy as np
import a2c
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.autograd as autograd
from torch.autograd import Variable

# Discount factor. Model is not very sensitive to this value.
GAMMA = .95

# LR of 3e-2 explodes the gradients, LR of 3e-4 trains slower
LR = 3e-3
N_GAMES = 2000

N_STEPS = 5

model = a2c.ActorCritic()
optimizer = optim.Adam(model.parameters(), lr=LR)


print ('Program started')
vrep.simxFinish(-1) # just in case, close all opened connections
clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5) # Connect to V-REP



if clientID!=-1:
	print ('Connected to remote API server')	
	emptyBuff = bytearray()
	
	"""
	res,retInts,retFloats,retStrings,retBuffer=vrep.simxCallScriptFunction(clientID,'Omega_test',vrep.sim_scripttype_childscript,'moveOmega_function',[10],[],[],emptyBuff,vrep.simx_opmode_blocking)
	if res==vrep.simx_return_ok:
		print ('Send command') # display the reply from V-REP (in this case, the handle of the created dummy)
	else:
		print ('Remote function call failed')
	"""
	
	finished_games = 0
	curr_step = 0
	
	state = np.array([0])
	done = False

	while finished_games < N_GAMES:
		states, actions, rewards, dones = [], [], [], []
		curr_step += 1
		# Gather training data
		for i in range(N_STEPS):
			# state: covered path
			s = Variable(torch.from_numpy(state).float().unsqueeze(0))

			action_probs = model.get_action_probs(s)
			#a = list(action_probs.size())
			#print(a)
			action = action_probs.multinomial(100).data[0][0]
			
			# take action
			res,retInts,retFloats,retStrings,retBuffer=vrep.simxCallScriptFunction(clientID,'Omega_test',vrep.sim_scripttype_childscript,'moveOmega_function',[action],[],[],emptyBuff,vrep.simx_opmode_blocking)
			if res==vrep.simx_return_ok:
				print ('action: ', action) # display the reply from V-REP (in this case, the handle of the created dummy)
			else:
				print ('Remote function call failed')
			
			# get state
			res,retInts,retFloats,retStrings,retBuffer=vrep.simxCallScriptFunction(clientID,'Omega_test',vrep.sim_scripttype_childscript,'getState_function',[],[],[],emptyBuff,vrep.simx_opmode_blocking)
			if res==vrep.simx_return_ok:
				print ('get state', retFloats[0]) # display the reply from V-REP (in this case, the handle of the created dummy)
			else:
				print ('Remote function call failed')
			
			next_state = retFloats[0]
			reward = retFloats[1]/curr_step
			if ((1.0-next_state)<0.01):
				done = True

			states.append(state); actions.append(action); rewards.append(reward); dones.append(done)

			if done: 
				# reset simulation
				res,retInts,retFloats,retStrings,retBuffer=vrep.simxCallScriptFunction(clientID,'Omega_test',vrep.sim_scripttype_childscript,'reset_function',[],[],[],emptyBuff,vrep.simx_opmode_blocking)
				if res==vrep.simx_return_ok:
					print ('reset') # display the reply from V-REP (in this case, the handle of the created dummy)
				else:
					print ('Remote function call failed')
				
				
				state = np.array([0])
				finished_games += 1 
				curr_step = 0
				done = False
				break
			else: 
				state = np.array(next_state)

		# Reflect on training data
		reflect(states, actions, rewards, dones)
	

	# Before closing the connection to V-REP, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
	vrep.simxGetPingTime(clientID)

	# Now close the connection to V-REP:
	vrep.simxFinish(clientID)
else:
	print ('Failed connecting to remote API server')

print ('Program ended')

def calc_actual_state_values(rewards, dones):
    R = []
    rewards.reverse()

    # If we happen to end the set on a terminal state, set next return to zero
    if dones[-1] == True: next_return = 0
        
    # If not terminal state, bootstrap v(s) using our critic
    # TODO: don't need to estimate again, just take from last value of v(s) estimates
    else: 
        s = torch.from_numpy(states[-1]).float().unsqueeze(0)
        next_return = model.get_state_value(Variable(s)).data[0][0] 
    
    # Backup from last state to calculate "true" returns for each state in the set
    R.append(next_return)
    dones.reverse()
    for r in range(1, len(rewards)):
        if not dones[r]: this_return = rewards[r] + next_return * GAMMA
        else: this_return = 0
        R.append(this_return)
        next_return = this_return

    R.reverse()
    state_values_true = Variable(torch.FloatTensor(R)).unsqueeze(1)
    
    return state_values_true

def reflect(states, actions, rewards, dones):
    
    # Calculating the ground truth "labels" as described above
    state_values_true = calc_actual_state_values(rewards, dones)

    s = Variable(torch.FloatTensor(states))
    action_probs, state_values_est = model.evaluate_actions(s)
    action_log_probs = action_probs.log() 
    
    a = Variable(torch.LongTensor(actions).view(-1,1))
    chosen_action_log_probs = action_log_probs.gather(1, a)

    # This is also the TD error
    advantages = state_values_true - state_values_est

    entropy = (action_probs * action_log_probs).sum(1).mean()
    action_gain = (chosen_action_log_probs * advantages).mean()
    value_loss = advantages.pow(2).mean()
    total_loss = value_loss - action_gain - 0.0001*entropy

    optimizer.zero_grad()
    total_loss.backward()
    nn.utils.clip_grad_norm(model.parameters(), 0.5)
    optimizer.step()
