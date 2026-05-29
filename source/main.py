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
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor

from . import constants as c
from . import setup, tools
from .states import level, load_screen, main_menu
from .states import controller_ppo
from .states import macro_ppo
import torch

def create_env(num_frames, frame_skip, use_macro, render):
    # Create an instance of the Control class from the 'tools' module
    game = tools.Control(num_frames, use_macro, render)

    rl = True

    # Create a dictionary mapping state names to their respective state instances
    state_dict = {
        c.MAIN_MENU: main_menu.Menu(),
        c.LOAD_SCREEN: load_screen.LoadScreen(rl),
        # c.LEVEL: level.Level(),
        c.LEVEL: level.Level(rl, num_frames, frame_skip, use_macro, render),
        c.GAME_OVER: load_screen.GameOver(),
        c.TIME_OUT: load_screen.TimeOut(),
    }

    # Setup the states of the game using the state dictionary and set the initial state to 'MAIN_MENU'
    game.setup_states(state_dict, c.MAIN_MENU)
    game.state.reset_game_info()
    game.state.done = True
    while type(game.state) is not level.Level:
        game.initial_step()
    if not rl:
        game.main()
    return game

# Define the main function of the script
def main(render):
    num_frames = 4
    frame_skip = 4
    use_macro = False
    run_without_learning = True
    runs = 5

    for i in range(1, runs+1):
        if use_macro:
            path = f"./macro{i}/"
        else:
            path = f"./controller{i}/"

        # Create an instance of the Control class from the 'tools' module
        env = create_env(num_frames, frame_skip, use_macro, render)

        if not run_without_learning:
            eval_env = create_env(num_frames, frame_skip, use_macro, render)
            eval_callback = EvalCallback(
                eval_env,
                eval_freq=10000,
                best_model_save_path=path,
                log_path=path,
                n_eval_episodes=5,
                deterministic=False,
            )

            if use_macro:
                Encoder = macro_ppo.MarioEncoder
            else:
                Encoder = controller_ppo.MarioEncoder
            policy_kwargs = dict(
                features_extractor_class=Encoder,
                features_extractor_kwargs=dict(features_dim=128),
            )

            if use_macro:
                Model = macro_ppo.MarioPPOWrapper
            else:
                Model = controller_ppo.MarioPPOWrapper
            model = PPO(
                policy=Model,
                env=env,
                policy_kwargs=policy_kwargs,
                learning_rate=1e-5,
                n_steps=2_048 // frame_skip,
                batch_size=64,
                n_epochs=2,
                gamma=0.99,
                verbose=int(render),
                ent_coef=0.04,
                device="cuda",
            )
        
        if run_without_learning:
            env = create_env(num_frames, frame_skip, use_macro, render)
            model = PPO.load("./controller5/best_model.zip", env=env, device="cuda")
            state, _ = env.reset()
            while True:
                action, _ = model.predict(state, deterministic=True)
                state, _,done,truncated = env.step(action)

        else:
            model.learn(total_timesteps=1_000_000, callback=eval_callback, progress_bar=True)
            model.save(f"{path}final_model")

           
        
        

