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

import os
from abc import ABC, abstractmethod
from enum import IntEnum, auto

import gymnasium as gym
import numpy as np
import pygame as pg
from gymnasium import spaces


class MacroMove(IntEnum):
    LEFT_ACTION = 0
    LEFT_ACTION_JUMP = auto()
    JUMP = auto()
    RIGHT_JUMP = auto()
    RIGHT_ACTION_JUMP = auto()
    RIGHT_ACTION = auto()
    RIGHT = auto()


# Dictionary defining keybindings for different actions
keybinding = {
    "action": pg.K_s,
    "jump": pg.K_SPACE,
    "left": pg.K_LEFT,
    "right": pg.K_RIGHT,
    "down": pg.K_DOWN,
}


# Class representing a State
class State:
    def __init__(self):
        # State variables
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.next = None
        self.persist = {}

    @abstractmethod
    def startup(self, current_time, persist):
        """Abstract method to be overridden in child classes"""

    def cleanup(self):
        # Reset the state after it's done
        self.done = False
        return self.persist

    @abstractmethod
    def update(self, surface, keys, current_time) -> tuple:
        """Abstract method to be overridden in child classes"""


# Class representing the Control for game states
class Control(gym.Env):
    def __init__(
        self, num_frames, use_macro, render, width=20, height=15, num_features=7, num_actions=7
    ):
        super().__init__()

        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(num_features * num_frames, height, width),
            dtype=np.float32,
        )

        self.do_render = render
        self.use_macro = use_macro

        if self.use_macro:
            self.action_space = spaces.Discrete(num_actions)
        else:
            self.action_space = spaces.MultiDiscrete([3, 2, 2])

        # Control variables
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60
        self.current_time = 0.0
        self.keys = pg.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.first_time = True

    def setup_states(self, state_dict, start_state):
        # Set up game states
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self, keys=None):
        if keys is None:
            keys = self.keys

        # Update current game state
        self.current_time = pg.time.get_ticks()
        if self.state.done:
            self.flip_state()

        return self.state.update(self.screen, keys, self.current_time)

    def flip_state(self):
        # Switch to the next game state
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)

    def event_loop(self):
        # Handle events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                exit(0)
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()

    def step(self, action):
        # init easy_keys
        keys = {}
        keys[keybinding["left"]] = False
        keys[keybinding["right"]] = False
        keys[keybinding["jump"]] = False
        keys[keybinding["down"]] = False
        keys[keybinding["action"]] = False

        if self.use_macro:
            match action:
                case MacroMove.RIGHT:
                    keys[keybinding["right"]] = True

                case MacroMove.JUMP:
                    keys[keybinding["jump"]] = True

                case MacroMove.LEFT_ACTION:
                    keys[keybinding["left"]] = True
                    keys[keybinding["action"]] = True

                case MacroMove.RIGHT_ACTION:
                    keys[keybinding["right"]] = True
                    keys[keybinding["action"]] = True

                case MacroMove.LEFT_ACTION_JUMP:
                    keys[keybinding["left"]] = True
                    keys[keybinding["action"]] = True
                    keys[keybinding["jump"]] = True

                case MacroMove.RIGHT_JUMP:
                    keys[keybinding["right"]] = True
                    keys[keybinding["jump"]] = True

                case MacroMove.RIGHT_ACTION_JUMP:
                    keys[keybinding["right"]] = True
                    keys[keybinding["action"]] = True
                    keys[keybinding["jump"]] = True

                case _:
                    print("Invalid macro action")
                    exit(1)
        else:
            keys[keybinding["left"]] = action[0] == 0
            keys[keybinding["right"]] = action[0] == 2
            keys[keybinding["jump"]] = action[1]
            keys[keybinding["down"]] = False
            keys[keybinding["action"]] = action[2]

        self.event_loop()
        result = None
        while result is None:
            result = self.update(keys)
        if self.do_render:
            pg.display.update()

        state, reward, done, truncated = result
        return state, reward, done, truncated, {}

    def reset(self, seed=None, options=None):
        print("RESET")
        if not self.first_time:
            self.state.update_game_info()
            self.state.done = True

        while True:
            self.event_loop()
            result = self.update()
            if result is not None:
                break

        self.first_time = False
        info = {}
        return result[0], info

    def initial_step(self):
        self.event_loop()
        self.update()
        if self.do_render:
            pg.display.update()

    def main(self):
        # Main game loop
        while not self.done:
            self.event_loop()
            self.update()
            if self.do_render:
                pg.display.update()
            self.clock.tick(60)


# Function to get an image from a sprite sheet
def get_image(sheet, x, y, width, height, colorkey, scale):
    image = pg.Surface([width, height])
    rect = image.get_rect()

    image.blit(sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(colorkey)
    image = pg.transform.scale(
        image, (int(rect.width * scale), int(rect.height * scale))
    )
    return image


# Function to load all graphics from a specified directory
def load_all_gfx(
    directory, colorkey=(255, 0, 255), accept=(".png", ".jpg", ".bmp", ".gif")
):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics
