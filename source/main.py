"""
MIT License

Copyright (c) [2023] [m0rniac]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__ = "m0rniac"

import pygame as pg
from stable_baselines3 import PPO

from . import constants as c
from . import setup, tools
from .states import level, load_screen, main_menu
from .states.ppo import MarioEncoder, MarioPPOWrapper


# Define the main function of the script
def main():
    # Create an instance of the Control class from the 'tools' module
    game = tools.Control()

    rl = True

    # Create a dictionary mapping state names to their respective state instances
    state_dict = {
        c.MAIN_MENU: main_menu.Menu(),
        c.LOAD_SCREEN: load_screen.LoadScreen(rl),
        # c.LEVEL: level.Level(),
        c.LEVEL: level.Level(rl),
        c.GAME_OVER: load_screen.GameOver(),
        c.TIME_OUT: load_screen.TimeOut(),
    }

    # Setup the states of the game using the state dictionary and set the initial state to 'MAIN_MENU'
    game.setup_states(state_dict, c.MAIN_MENU)
    game.state.reset_game_info()
    game.state.done = True
    while type(game.state) is not level.Level:
        game.initial_step()

    policy_kwargs = dict(
        features_extractor_class=MarioEncoder,
        features_extractor_kwargs=dict(features_dim=128),
    )

    model = PPO(
        policy=MarioPPOWrapper,
        env=game,
        policy_kwargs=policy_kwargs,
        learning_rate=0.0003,
        n_steps=2_048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        verbose=1,
    )

    model.learn(total_timesteps=1_000_000)

    # Start the main game loop
    # game.main()
