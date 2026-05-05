# This code is partially from Alexander Scheerder (a member of this game ai group), this code was partially used in an reinforcement learning assignment it is reused.

# import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import pygame as pg
from source.main import main

from source.states.helper import evaluate

class env:
    def __init__(self):
        # make env

        # start game
        print("Main started")
        main()
        print("main done")
        pg.quit()
        # turn level on

        # init all self vars
        self.state = []
        self.action_space = []


    def reset(self, seed=42):
        # reset env

        # get begin state
        # update self.state

        return self.state

    def observation_space(self):
        # get amount of different values (determines the network architecture)

        return obseraction_space
    
    def action_space(self):
        # return action space size

        return action_space_size
    
    def random_action(self):
        # return random chosen action
        return action

    def step(self, action):
        # perform action in environment, update environent and return: next_state, reward, terminated, truncated and
        
        next_state = something
        # update self.state
        self.state = next_state

        return next_state, reward, terminated, truncated
    
    def close(self):
        # close environent (close pygame etc.)
        return


class CartPoleEnv:
    def __init__(self, render=False, seed=42):
        self.render_mode = "human" if render else None
        # self.env = gym.make("CartPole-v1", render_mode=self.render_mode)
        self.env = env()
        # self.state, _ = self.env.reset(seed=seed)
        self.state = self.env.reset(seed=seed)

        # self.state_size = self.env.observation_space.shape[0]
        self.state_size = self.env.observation_space()
        # self.action_size = self.env.action_space.n
        self.action_size = self.env.action_space()
        # self.env.action_space.seed(seed)

    def reset(self):
        # self.state, _ = self.env.reset()
        self.state = self.env.reset()
        return self.state

    def step(self, action):
        # next_state, reward, terminated, truncated, _ = self.env.step(action)
        next_state, reward, terminated, truncated = self.env.step(action)
        done = terminated or truncated
        return next_state, reward, done

    def sample_action(self):
        # return self.env.action_space.sample()
        return self.env.random_action()

    def close(self):
        self.env.close()


class π_θ(nn.Module):
    def __init__(self, state_size, action_size, network_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, network_size),
            nn.ReLU(),
            nn.Linear(network_size, network_size),
            nn.ReLU(),
            nn.Linear(network_size, action_size),
            nn.Softmax(dim=-1),
        )

    def forward(self, x):
        return self.net(x)


class V_network(nn.Module):
    def __init__(self, state_size, action_size, network_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_size, network_size),
            nn.ReLU(),
            nn.Linear(network_size, network_size),
            nn.ReLU(),
            nn.Linear(network_size, action_size),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def PPO_clipped_train(gamma, learning_rate, max_steps, network_size, epsilon, epochs):
    # placeholder ppo
            

    env.close()
    return returns, step_list


if __name__ == "__main__":
    # run example
    gamma = 1.0
    learning_rate = 1e-3
    max_steps = 2001
    network_size = 64
    res = []
    epsilon = 0.2
    epochs = 10
    for _ in range(5):
        results, _ = PPO_clipped_train(gamma, learning_rate, max_steps, network_size, epsilon, epochs)
        res.append(results)
    mean_return = np.mean(np.array(res),axis=0)
    print(f"The mean return per eval over 5 repetitions: {mean_return}")
    

