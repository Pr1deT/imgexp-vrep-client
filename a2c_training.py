
import a2c
import RLsetup

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.autograd as autograd
from torch.autograd import Variable

import numpy as np

# Discount factor. Model is not very sensitive to this value.
GAMMA = .95
LR = 3e-3
model = a2c.ActorCritic()
optimizer = optim.Adam(model.parameters(), lr=LR)

N_GAMES = 2000
N_STEPS = 5
N_ACTIONS = 8

env = RLsetup.imgexp()

def train():
	state = env.reset() 
	finished_games = 0

	while finished_games < N_GAMES:

		states, actions, rewards, dones = [], [], [], []

		# Gather training data
		for i in range(N_STEPS):
			# state
			flat_state = [item for sublist in state for item in sublist]
			state = np.array(flat_state)
			s = Variable(torch.from_numpy(state).float().unsqueeze(0))

			action_probs = model.get_action_probs(s)
			action = action_probs.multinomial(N_ACTIONS).data[0][0]
			print 'action: ', action
			next_state, reward, done, _ = env.step(action)
			#print 'next state ', next_state
			print 'reward ', reward
			#print 'done ', done

			states.append(state); actions.append(action); rewards.append(reward); dones.append(done)

			if done: 
				state = env.reset()
				finished_games += 1
			else: state = next_state

		# Reflect on training data
		reflect(states, actions, rewards, dones)

def reflect(states, actions, rewards, dones):
	
	# Calculating the ground truth "labels" as described above
	state_values_true = calc_actual_state_values(states,rewards, dones)

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

def calc_actual_state_values(states, rewards, dones):
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

if __name__ == '__main__':
	train()


