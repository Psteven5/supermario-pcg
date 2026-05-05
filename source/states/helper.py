# This code is reused from an Reinforcement assignment! This code is written by some members of the group and is thus reused for this assignment.

import torch
import numpy as np

def evaluate(model,eval_env,n_eval_episodes=30):
    returns = []  # list to store the reward per episode

    for i in range(n_eval_episodes):
        s = eval_env.reset()
        state = torch.tensor(s, dtype=torch.float32)
        R_ep = 0
        done = False
        while not done:
            action = torch.argmax(model(state)).item()
            next_state, reward, done = eval_env.step(action)
            R_ep += reward
            if done:
                break
            else:
                next_state = torch.tensor(next_state, dtype=torch.float32)
                state = next_state
        returns.append(R_ep)
    mean_return = np.mean(returns)
    return mean_return