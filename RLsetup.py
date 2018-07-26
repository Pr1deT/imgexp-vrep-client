"""
Reinforcement Learning Setup
"""

import vrepsim
import numpy as np
import random
import math

DONE_STEPS = 100

pctg_list = [25,50,75,100]
gama_list = [0,90,180,270]

class imgexp(object):
	def __init__(self):
		self.sim = vrepsim.vrepsim()
		self.commands = ['go_straight', 'path']
		self.decide_type = range(3)
		self.pos_x = range(400)
		self.pos_y = range(261) 
		self.num_steps = 0
		self.img_width = 0
		self.img_height = 0
		self.state = self.reset()



	def reset(self):
		state = []
		if (self.sim.reset()):
			cur_x, cur_y = self.sim.init_pos[0],self.sim.init_pos[1]
			state = [[cur_x, cur_y], # current omega position
					 [0,0], 		 # image width, height
					 [0,-1,-1,-1,-1],		 # white: cell type, location (left, right, up, down)
					]
		self.accuracy = 0.0
		self.num_steps = 0
		self.size = 0.0

		return state

	def step(self,action):
		info = ''
		next_state = self.state
		action_list, value_range = self.sim.get_possible_action_list() 
		#print 'action list: ', action_list
		#print 'value range: ', value_range
		action = int(action)
		a = len(gama_list)
		if action in range(a):
			command = 'go_straight'
			value = gama_list[action]
			
		elif action in range(a,a+len(pctg_list)):
			command = 'path'
			value = pctg_list[action-a]
			value_range = range(101)

		print 'command: ', command
		print 'value: ', value

		if (command in action_list) and (value in value_range):
			self.this_command = [command,value]
			
			if (self.this_command[0]=='path'):
				st_state, ed_state = self.sim.step(command,0,value)
				if abs(value-100)<=30:
					next_state[2][0] = 1
			else:
				st_state, ed_state = self.sim.step(command,value)
				next_state = self.update_state(st_state,ed_state)
			
			reward = self.compute_reward(self.state, next_state)
			next_state[0] = ed_state[1:3]
			self.state = next_state

		else:
			# negative rewards ??
			self.this_command = ['invalid',0]
			reward = 0.01
			

		self.num_steps += 1
		done = False
		if (self.is_done(next_state)):
			done = True
		
		return next_state, reward, done, info

	def update_state(self, st_state, ed_state):
		state = self.state

		start_type, start_loc = st_state[0].split('_')
		end_type, end_loc = ed_state[0].split('_')

		x0, y0 = st_state[1], st_state[2]
		x1, y1 = ed_state[1], ed_state[2]

		x = abs(x1-x0) 
		y = abs(y1-y0)
		
		# decide ep
		if (start_type=='wall' and end_type=='wall'):
			# frame following
			width = abs(x1-x0) 
			height = abs(y1-y0)

			if (width > self.img_width):
				state[1][0] = width
			if (height > self.img_height):
				state[1][1] = height

		# absolut positioning
		else:
			# target cell: cell
			# side of wall: start_loc 
			if (start_type=='cell'):
				cell = start_loc
				start_loc = end_loc
			else:
				cell = end_loc
			
			# get target cell index
			cell_index = self._get_cell_index(cell)
			# get wall index
			wall_index = self._get_wall_index(start_loc)

			# compute distance between cell and the side of wall
			dist = math.sqrt( (x0 - x1)**2 + (y0 - y1)**2 )
			# update state
			state[cell_index][wall_index] = dist

		return state

	def compute_reward(self, prev_state, state):
		reward = 0.0
		# know cell type
		if (prev_state[2][0]==0 and state[2][0]==1):
			reward += 5
			self.size = self.sim.get_obj_size('red')

		x0,y0 = prev_state[0]
		x1,y1 = state[0]
		motion_dist = math.sqrt((x0 - x1)**2 + (y0 - y1)**2)

		reward += motion_dist

		# distance knowledge in x
		if prev_state[1][0]!=state[1][0] and abs(state[1][0]-399)<=30:
			reward += 5
		if prev_state[1][1]!=state[1][1] and abs(state[1][1]-260)<=30:
			reward += 5

		if state[1][0]> prev_state[1][0]:
			reward += 2
		if state[1][1]> prev_state[1][1]:
			reward += 2

		if (state[2][1]+state[2][2]<=state[1][0]):
			reward += 0.5
		# distance knowledge in y
		if (state[2][3]+state[2][4]<=state[1][1]):
			reward += 0.5

		# compute accuracy from state
		accuracy_x = 1.0 * (state[2][1]+state[2][2]+self.size)/399.0
		accuracy_y = 1.0 * (state[2][3]+state[2][4]+self.size)/266.0
		self.accuracy = (accuracy_y+accuracy_x)/2.0

		if (self.accuracy>=0.7):
			reward += 10

		print 'state: ', state

		return reward

	def is_done(self, state):
		if (self.num_steps >= DONE_STEPS):
			print 'steps: ', self.num_steps
			print 'done: ', self.accuracy
			return True

		# accuracy > 0.9
		if (self.accuracy>0.7):
			print 'accuracy: ', self.accuracy
			print 'done: ', self.accuracy
			return True


		return False

	def _get_cell_index(self, cell_type):
		index = -1
		if (cell_type=='white'):
			index = 3
		else:
			index = 2
		return index

	def _get_wall_index(self, wall_type):
		index = -1
		if (wall_type=='top'):
			index = 3
		elif (wall_type=='bottom'):
			index = 4
		elif (wall_type=='left'):
			index = 1
		elif (wall_type=='right'):
			index = 2

		return index






