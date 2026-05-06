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

__author__ = 'm0rniac'

from .. import setup, tools
from .. import constants as c
from ..components import info

class LoadScreen(tools.State):
    def __init__(self, rl: bool = False):
        super().__init__()
        if rl:
            self.time_list = [0, 0, 0]
        else:
            self.time_list = [2400, 2600, 2635]

    def startup(self, current_time, persist):
        # Initialize the state with necessary variables
        self.start_time = current_time
        self.persist = persist
        self.game_info = self.persist
        self.next = self.set_next_state()

        # Set up the overhead info for displaying game information
        info_state = self.set_info_state()
        self.overhead_info = info.Info(self.game_info, info_state)

    def set_next_state(self):
        # Return the next state after LoadScreen
        return c.LEVEL

    def set_info_state(self):
        # Return the type of info state to be displayed
        return c.LOAD_SCREEN

    def update(self, surface, keys, current_time):
        # Update the load screen according to the time elapsed
        if (current_time - self.start_time) < self.time_list[0]:
            self.draw_load_screen(surface, c.BLACK)
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        elif (current_time - self.start_time) < self.time_list[1]:
            self.draw_load_screen(surface, c.BLACK)
        elif (current_time - self.start_time) < self.time_list[2]:
            self.draw_load_screen(surface, (106, 150, 252))
        else:
            self.done = True

    def draw_load_screen(self, surface, color):
        # Helper function to fill the surface with a specific color
        surface.fill(color)

class GameOver(LoadScreen):
    def __init__(self):
        super().__init__()
        self.time_list = [3000, 3200, 3235]

    def set_next_state(self):
        # Override the next state after GameOver
        return c.MAIN_MENU

    def set_info_state(self):
        # Override the info state to be displayed after GameOver
        return c.GAME_OVER

class TimeOut(LoadScreen):
    def __init__(self):
        super().__init__()
        self.time_list = [2400, 2600, 2635]

    def set_next_state(self):
        # Determine the next state after TimeOut based on remaining lives
        if self.persist[c.LIVES] == 0:
            return c.GAME_OVER
        else:
            return c.LOAD_SCREEN

    def set_info_state(self):
        # Override the info state to be displayed after TimeOut
        return c.TIME_OUT
