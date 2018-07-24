"""
Reinforcement Learning Setup
"""

import vrepsim
import numpy as np
import random

class imgexp(object):
	def __init__(self):
		self.sim = vrepsim()
		self.commands = ['go_straight', 'path']
		self.decide_type = range(3)
		self.pos_x = range(400)
		self.pos_y = range(261) 
		self.num_steps = 0
		self.img_width = 0
		self.img_height = 0
		self.state = self.reset()



	def get_action_list(self,pos):
		if (pos=='img'):

	def reset(self):
		state = []
		if (self.sim.reset()):
			state = [[cur_x, cur_y], # current omega position
					 [0,0], 		 # image width, height
					 [0,-1,-1,-1,-1],		 # white: cell type, location (left, right, up, down)
					 [0,-1,-1,-1,-1]		 # red: another cell
					]

		return state

	def step(self,action):
		info = ''
		action_list, value_range = get_action_list() #??

		if action in range(0,360):
			command = 'go_straight'
			value = action
			
		elif action in range(360,460):
			command = 'path'
			value = action - 360

		if (command in action_list) and (value in gama_range):
			self.this_command = [command,value]
			st_state, ed_state = self.sim.step(command,value)

		else:
			# negative rewards ??
			self.this_command = ['invalid',0]
			reward = -1.0

		self.num_steps += 1
		done = False
		if (self.num_steps >= DONE_STEPS):
			done = True

		next_state = self.update_state()


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
				state[1,0] = width
			if (height > self.img_height):
				state[1,1] = height

		elif (start_type=='cell' and end_type=='cell'):
			if (start_loc==end_loc):
				# contour following
				index = self._get_cell_index(start_loc)
				state[index,0] = 2 # update cell type knowledge
			else:
				# relative positioning
				start_index = self._get_cell_index(start_loc)
				end_index = self._get_cell_index(end_loc)
				# unknown x
				if (not (state[2][1]==-1)):
					state[3][1] = x
				if 

				if (state[start_index,2]==-1):
					state[start_index,2] = random.randint(0,state[1,1])

				if (state[end_index,1]==-1):
					state[end_index,1] = random.randint(0,state[1,0])
				if (state[end_index,2]==-1):
					state[end_index,2] = random.randint(0,state[1,1])
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
			dist = sqrt( (x0 - x1)**2 + (y0 - y1)**2 )
			# update state
			state[cell_index][wall_index] = dist

		return state

	def _get_cell_index(cell_type):
		index = -1
		if (cell_type=='white'):
			index = 2
		else:
			index = 3
		return index

	def _get_wall_index(wall_type):
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






