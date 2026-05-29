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

import json
import os
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from pprint import pprint

# RL agent import
# import gymnasium as gym
import numpy as np
import pygame as pg
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

from .. import constants as c
from .. import setup, tools
from ..tools import keybinding
from ..components import box, brick, coin, enemy, info, player, powerup, stuff, ground, step
from . import generate_chunk


class MacroMove(Enum):
    LEFT = 0
    RIGHT = auto()
    ACTION = auto()
    JUMP = auto()
    LEFT_ACTION = auto()
    RIGHT_ACTION = auto()
    LEFT_JUMP = auto()
    RIGHT_JUMP = auto()
    LEFT_ACTION_JUMP = auto()
    RIGHT_ACTION_JUMP = auto()


class EntityType(Enum):
    PLAYER = 0
    GROUND = auto()
    BRICK = auto()
    BOX = auto()
    ENEMY = auto()
    POWERUP = auto()


@dataclass
class Entity:
    x: int
    y: int
    w: int
    h: int
    dx: int
    dy: int
    ty: EntityType

class EntityType(Enum):
    PLAYER = 0
    GROUND = auto()
    BRICK = auto()
    BOX = auto()
    ENEMY = auto()
    POWERUP = auto()


@dataclass
class Entity:
    x: int
    y: int
    w: int
    h: int
    dx: int
    dy: int
    ty: EntityType



# Define a class for the level state, which inherits from tools.State
class Level(tools.State):
    def __init__(self, rl, num_frames, frame_skip, use_macro, render):
        tools.State.__init__(self)
        self.player = None
        self.max_x = 0.0
        self.reward = 0.0

        self.shift_threshold = c.SHIFT_THRESHOLD + c.SCREEN_WIDTH
        self.reset = True

        self.last_x = 0.0
        self.best_x = 0
        self.jump_count = 0
        self.top_score = 0
        self.last_time = 0
        self.dx = 0
        self.idle = 0
        self.steps = 0
        self.render = render
        self.use_macro = use_macro

        self.death_timeout = 0 if rl else 3000
        self.live_change_on_death = 0 if rl else 1

        self.state_queue = deque(maxlen=num_frames)
        self.frame_skip = frame_skip

    # Function to initialize the level state
    def startup(self, current_time, persist):

        # Initialize game information
        self.game_info = persist
        self.persist = self.game_info
        self.death_timer = 0
        self.castle_timer = 0

        # Initialize variables for reward calculation ~ alexReward
        self.prev_reward = 0.0
        self.count = 1
        self.max_x = 0.0
        self.dx = 0
        self.prev_score = self.game_info[c.SCORE]
        self.reward = 0.0
        self.prev_x = 110.0
        self.prev_y = 0.0
        self.idle = 0
        self.jumptimer = 0
        self.left_bound = 0
        self.mario_pos = 0

        #skill tracking
        self.chunk_start_time = current_time
        self.chunk_time = 0
        self.forward_speed_sum = 0
        self.forward_speed_frames = 0
        self.avg_forward_speed = 0
        self.skill = 1.0
        self.diff_skill = 0
        self.recent_chunk_times = []
        self.recent_chunk_speeds = []

        # Initialize lists and overhead information
        self.moving_score_list = []
        self.overhead_info = info.Info(self.game_info, c.LEVEL)

        # Load map data and set up background
        self.chunk_size = c.CHUNK_SIZE
        chunk_chances = {"gaps": c.CHANCE_GAP,
                         "pipestairs": c.CHANCE_PIPESTAIRS,
                         "bricks": c.CHANCE_BRICKS,
                         "boxes": c.CHANCE_BOXES,
                         "enemies": c.CHANCE_ENEMIES,
                         "chunk_bricks": c.CHANCE_BRICKS_CHUNK,
                         "chunk_split": c.CHANCE_SPLIT_CHUNK}
        generator = generate_chunk.GenerateChunk(self.chunk_size, chunk_chances)
        generator.generate_chunk(first=True)
        self.load_map()
        self.setup_background()
        self.setup_maps()

        # Initialize variables for reward calculation ~ pieterReward
        self.last_x = self.player_x
        self.best_x = self.player_x
        self.top_score = self.persist[c.SCORE]
        self.last_time = self.persist[c.CURRENT_TIME]
        self.jump_count = 0
        self.steps = 0

        # Set up various sprite groups for collisions and interactions
        self.ground_group = self.setup_collide(c.MAP_GROUND)
        self.step_group = self.setup_collide(c.MAP_STEP)
        self.setup_pipe()
        self.setup_slider()
        self.setup_static_coin()
        self.setup_brick_and_box()
        self.setup_player()
        self.setup_enemies()
        self.setup_checkpoints()
        self.setup_flagpole()
        self.setup_sprite_groups()

    # Function to load the map data from a JSON file
    def load_map(self):
        # # TODO: choose level 1 or pcg
        map_file = "level_" + str(self.game_info[c.LEVEL_NUM]) + ".json"
        # file_path = os.path.join("source", "data", "maps", map_file)

        # TODO: change this function and use it in load_next_chunk?
        # map_file = "chunk.json"
        file_path = os.path.join("source", "data", "maps", map_file)
        f = open(file_path)
        self.map_data = json.load(f)
        f.close()

        # Keep track of the base chunk to add this later for infinite level
        self.base_data = self.map_data.copy()
        self.current_chunk = 0
        self.chunk_size = c.CHUNK_SIZE

    def check_for_chunk(self):
        # build next chunk when halfway current chunk
        if self.player.rect.x > self.chunk_size/2 and self.reset:
            self.reset = False
            if self.current_chunk > 0:
                self.chunk_time = (self.current_time - self.chunk_start_time) / 1000 # in seconds

                if self.forward_speed_frames > 0:
                    self.avg_forward_speed = self.forward_speed_sum / self.forward_speed_frames
                else:
                    self.avg_forward_speed = 0

                avg_time = sum(self.recent_chunk_times) / len(self.recent_chunk_times) if self.recent_chunk_times else self.chunk_time
                avg_speed = sum(self.recent_chunk_speeds) / len(self.recent_chunk_speeds) if self.recent_chunk_speeds else self.avg_forward_speed

                self.recent_chunk_times.append(self.chunk_time)
                self.recent_chunk_speeds.append(self.avg_forward_speed)
                # keep only last 5 chunks
                self.recent_chunk_times = self.recent_chunk_times[-5:]
                self.recent_chunk_speeds = self.recent_chunk_speeds[-5:]

                time_score = avg_time / (self.chunk_time + 1e-6)
                speed_score = self.avg_forward_speed / (avg_speed + 1e-6)

                previous_skill = self.skill
                self.skill = 0.6*speed_score + 0.4*time_score

                self.diff_skill = self.skill - previous_skill

                print(f"Chunk time: {self.chunk_time:.2f}s, Avg time: {avg_time:.2f}s, Time score: {time_score:.2f}, Avg speed: {avg_speed:.2f}, Speed score: {speed_score:.2f}, Overall skill: {self.skill:.2f}, diff_skill: {self.diff_skill:.2f}")

            self.chunk_start_time = self.current_time
            self.forward_speed_sum = 0
            self.forward_speed_frames = 0

            self.current_chunk += 1
            self.chunk_size = c.CHUNK_SIZE

            # Chances for different level components (between 0.0 and 1.0)
            # given an array chances:
            # 0 - gaps, 1 - pipe/stairs, 2 - bricks, 3 - boxes, 4 - enemies

            chunk_chances = dict()
            k = 0.15 # how quickly we increase the difficulty

            # difficulty between 0 and 5 (base is going from 0 to 5)
            base = self.get_difficulty(k, self.current_chunk)
            difficulty = base + self.diff_skill
            difficulty = np.clip(difficulty, 0, c.MAX_DIFFICULTY)

            print(f"Chunk: {self.current_chunk}, Difficulty: {difficulty:.2f}")
            norm_diff = difficulty / 5

            chunk_chances["gaps"] = (c.CHANCE_GAP + (c.END_CHANCE_GAP - c.CHANCE_GAP) * (norm_diff ** c.WEIGHT_GAP))
            chunk_chances["pipestairs"] = (c.CHANCE_PIPESTAIRS + (c.END_CHANCE_PIPESTAIRS - c.CHANCE_PIPESTAIRS) * (norm_diff ** c.WEIGHT_PIPESTAIRS))
            chunk_chances["bricks"] = (c.CHANCE_BRICKS + (c.END_CHANCE_BRICKS - c.CHANCE_BRICKS) * (norm_diff ** c.WEIGHT_BRICKS)) #linear increasing
            chunk_chances["boxes"] = (c.CHANCE_BOXES + (c.END_CHANCE_BOXES - c.CHANCE_BOXES) * (norm_diff ** c.WEIGHT_BOXES)) #decreasing
            chunk_chances["enemies"] = (c.CHANCE_ENEMIES + (c.END_CHANCE_ENEMIES - c.CHANCE_ENEMIES) * (norm_diff ** c.WEIGHT_ENEMIES))
            chunk_chances["chunk_bricks"] = (c.CHANCE_BRICKS_CHUNK + (c.END_CHANCE_BRICKS_CHUNK - c.CHANCE_BRICKS_CHUNK) * (norm_diff ** c.WEIGHT_BRICKS_CHUNK))
            chunk_chances["chunk_split"] = (c.CHANCE_SPLIT_CHUNK + (c.END_CHANCE_SPLIT_CHUNK - c.CHANCE_SPLIT_CHUNK) * (norm_diff ** c.WEIGHT_SPLIT_CHUNK))

            generator = generate_chunk.GenerateChunk(self.chunk_size, chunk_chances, difficulty=difficulty)
            generator.generate_chunk()
            self.load_next_chunk()
        if self.viewport.x > self.shift_threshold:
            self.reset = True
            self.reset_map(self.chunk_size)

    def get_difficulty(self, k, chunk_num):
        return c.MAX_DIFFICULTY * (1 - c.EULER_NUM**(-k * chunk_num))


    def load_next_chunk(self, ):
        # TODO: use load_map to change self.map_data to new level from generated new json file?
        offset_x = self.chunk_size
        map_file = "chunk.json"
        file_path = os.path.join("source", "data", "maps", map_file)
        f = open(file_path)
        new_map_data = json.load(f)
        f.close()
        for data in new_map_data:
            if isinstance(new_map_data[data], list):
                for item in new_map_data[data]:
                    if isinstance(item, dict) and "x" in item:
                        item["x"] += offset_x
                    elif isinstance(item, dict) and "start_x" in item:
                        item["start_x"] += offset_x
                        item["end_x"] += offset_x
                    elif isinstance(item, dict):
                        for key in item:
                            if isinstance(item[key], list):
                                for enemy_item in item[key]:
                                    if isinstance(enemy_item, dict) and "x" in enemy_item:
                                        enemy_item["x"] += offset_x
        self.add_chunk_to_map_data(new_map_data)

    def add_chunk_to_map_data(self, map_data):
        #TODO: make use of existing functions (change functions a bit)
        enemy_group_offset = len(self.enemy_group_list)

        if c.MAP_GROUND in map_data:
            for item in map_data[c.MAP_GROUND]:
                collider = stuff.Collider(item["x"], item["y"], item["width"], item["height"], c.MAP_GROUND)
                collider.image = pg.Surface((collider.rect.width, collider.rect.height))
                collider.image.fill((0, 0, 0))
                self.ground_group.add(collider)
                for y in range(item["y"], item["y"] + item["height"], 43):
                    for x in range(item["x"], item["x"] + item["width"], 43):
                        self.ground_group.add(ground.Ground(x, y))

        if c.MAP_PIPE in map_data:
            for item in map_data[c.MAP_PIPE]:
                self.pipe_group.add(stuff.Pipe(item["x"], item["y"], item["width"], item["height"], item["type"]))

        if c.MAP_COIN in map_data:
            for item in map_data[c.MAP_COIN]:
                self.static_coin_group.add(coin.StaticCoin(item["x"], item["y"]))

        if c.MAP_BRICK in map_data:
            for item in map_data[c.MAP_BRICK]:
                brick.create_brick(self.brick_group, item, self)

        if c.MAP_BOX in map_data:
            for item in map_data[c.MAP_BOX]:
                if item["type"] == c.TYPE_COIN:
                    self.box_group.add(box.Box(item["x"], item["y"], item["type"], self.coin_group))
                else:
                    self.box_group.add(box.Box(item["x"], item["y"], item["type"], self.powerup_group))

        if c.MAP_ENEMY in map_data:
            for data in map_data[c.MAP_ENEMY]:
                group = pg.sprite.Group()
                for key in data:
                    for item in data[key]:
                        group.add(enemy.create_enemy(item, self))
                self.enemy_group_list.append(group)

        if c.MAP_CHECKPOINT in map_data:
            for data in map_data[c.MAP_CHECKPOINT]:
                if c.ENEMY_GROUPID in data:
                    enemy_groupid = data[c.ENEMY_GROUPID] + enemy_group_offset
                else:
                    enemy_groupid = 0
                if c.MAP_INDEX in data:
                    map_index = data[c.MAP_INDEX]
                else:
                    map_index = 0
                self.checkpoint_group.add(stuff.Checkpoint(data["x"], data["y"], data["width"],
                    data["height"], data["type"], enemy_groupid, map_index))

        if c.MAP_FLAGPOLE in map_data:
            for item in map_data[c.MAP_FLAGPOLE]:
                if item["type"] == c.FLAGPOLE_TYPE_FLAG:
                    sprite = stuff.Flag(item["x"], item["y"])
                    self.flag = sprite
                elif item["type"] == c.FLAGPOLE_TYPE_POLE:
                    sprite = stuff.Pole(item["x"], item["y"])
                else:
                    sprite = stuff.PoleTop(item["x"], item["y"])
                self.flagpole_group.add(sprite)

        if c.MAP_STEP in map_data:
            for item in map_data[c.MAP_STEP]:
                collider = stuff.Collider(item["x"], item["y"], item["width"], item["height"], c.MAP_STEP)
                collider.image = pg.Surface((collider.rect.width, collider.rect.height))
                self.step_group.add(collider)
                for y in range(item["y"], item["y"] + item["height"], 43):
                    for x in range(item["x"], item["x"] + item["width"], 43):
                        self.step_group.add(step.Step(x, y))

        if c.MAP_SLIDER in map_data:
            for item in map_data[c.MAP_SLIDER]:
                if c.VELOCITY in item:
                    vel = item[c.VELOCITY]
                else:
                    vel = 1
                self.slider_group.add(stuff.Slider(item["x"], item["y"], item["num"],
                    item["direction"], item["range_start"], item["range_end"], vel))

        self.ground_step_pipe_group.add(
            self.pipe_group,
            self.ground_group,
            self.step_group,
            self.slider_group
        )
    def delete_old_sprites(self):
        limit = self.viewport.x - c.SCREEN_WIDTH

        for group in [self.ground_group, self.step_group, self.pipe_group, self.slider_group,
                    self.static_coin_group, self.brick_group, self.box_group, self.enemy_group, self.shell_group,
                    self.powerup_group, self.coin_group, self.brickpiece_group,
                    self.checkpoint_group, self.flagpole_group, self.dying_group]:
            for sprite in group:
                if sprite.rect.right < limit:
                    sprite.kill()
    def reset_map(self, offset):
        # Shift player
        self.mario_pos += self.player.rect.x
        self.player.rect.x -= offset
        self.last_x -= offset
        self.best_x -= offset
        # Shift viewpoint
        self.viewport.x -= offset

        # Update background offset
        self.bg_offset = (self.bg_offset + offset) % self.background.get_width()

        self.left_bound -= offset

        # shift all sprites
        for group in [self.ground_group, self.step_group, self.pipe_group, self.slider_group,
                    self.static_coin_group, self.brick_group, self.box_group, self.enemy_group, self.shell_group,
                    self.powerup_group, self.coin_group, self.brickpiece_group,
                    self.checkpoint_group, self.flagpole_group, self.dying_group]:
            for sprite in group:
                sprite.rect.x -= offset

        for group in self.enemy_group_list:
            for sprite in group:
                if sprite not in self.enemy_group:
                    sprite.rect.x -= offset


    # Function to set up the level background
    def setup_background(self):
        img_name = self.map_data[c.MAP_IMAGE]
        self.background = setup.GFX[img_name]
        self.bg_rect = self.background.get_rect()
        self.background = pg.transform.scale(
            self.background,
            (
                int(self.bg_rect.width * c.BACKGROUND_MULTIPLER),
                int(self.bg_rect.height * c.BACKGROUND_MULTIPLER),
            ),
        )
        self.bg_rect = self.background.get_rect()
        self.bg_offset = 0

        self.level = pg.Surface((self.chunk_size*2, c.SCREEN_HEIGHT)).convert()
        self.viewport = setup.SCREEN.get_rect(bottom=self.bg_rect.bottom)

    # Function to set up the different maps for the level
    def setup_maps(self):
        self.map_list = []
        if c.MAP_MAPS in self.map_data:
            for data in self.map_data[c.MAP_MAPS]:
                self.map_list.append(
                    (data["start_x"], data["end_x"], data["player_x"], data["player_y"])
                )
            self.start_x, self.end_x, self.player_x, self.player_y = self.map_list[0]
        else: #TODO not used???
            self.start_x = 0
            self.end_x = self.chunk_size
            self.player_x = 110
            self.player_y = c.GROUND_HEIGHT

    # Function to change the current map to a new one based on a checkpoint
    def change_map(self, index, type):
        self.start_x, self.end_x, self.player_x, self.player_y = self.map_list[index]
        self.viewport.x = self.start_x
        if type == c.CHECKPOINT_TYPE_MAP:
            self.player.rect.x = self.viewport.x + self.player_x
            self.player.rect.bottom = self.player_y
            self.player.state = c.STAND
        elif type == c.CHECKPOINT_TYPE_PIPE_UP:
            self.player.rect.x = self.viewport.x + self.player_x
            self.player.rect.bottom = c.GROUND_HEIGHT
            self.player.state = c.UP_OUT_PIPE
            self.player.up_pipe_y = self.player_y

    # Function to set up collision groups for various map elements
    def setup_collide(self, name):
        group = pg.sprite.Group()
        if name in self.map_data:
            for data in self.map_data[name]:
                collider = stuff.Collider(data["x"], data["y"], data["width"], data["height"], name)
                collider.image = pg.Surface((collider.rect.width, collider.rect.height))
                collider.image.fill((0, 0, 0))
                group.add(collider)
                # green = ground, brown = steps
                if name == c.MAP_GROUND:
                    for y in range(data["y"], data["y"] + data["height"], 43):
                        for x in range(data["x"], data["x"] + data["width"], 43):
                            group.add(ground.Ground(x,y))
                else:
                    for y in range(data["y"], data["y"] + data["height"], 43):
                        for x in range(data["x"], data["x"] + data["width"], 43):
                            group.add(step.Step(x,y))
        return group

    # Function to set up pipe objects on the map
    def setup_pipe(self):
        self.pipe_group = pg.sprite.Group()
        if c.MAP_PIPE in self.map_data:
            for data in self.map_data[c.MAP_PIPE]:
                self.pipe_group.add(
                    stuff.Pipe(
                        data["x"],
                        data["y"],
                        data["width"],
                        data["height"],
                        data["type"],
                    )
                )

    # Function to set up slider objects on the map
    def setup_slider(self):
        self.slider_group = pg.sprite.Group()
        if c.MAP_SLIDER in self.map_data:
            for data in self.map_data[c.MAP_SLIDER]:
                if c.VELOCITY in data:
                    vel = data[c.VELOCITY]
                else:
                    vel = 1
                self.slider_group.add(
                    stuff.Slider(
                        data["x"],
                        data["y"],
                        data["num"],
                        data["direction"],
                        data["range_start"],
                        data["range_end"],
                        vel,
                    )
                )

    def setup_static_coin(self):
        self.static_coin_group = pg.sprite.Group()
        if c.MAP_COIN in self.map_data:
            for data in self.map_data[c.MAP_COIN]:
                self.static_coin_group.add(coin.StaticCoin(data["x"], data["y"]))

    def setup_brick_and_box(self):
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.Group()
        self.brick_group = pg.sprite.Group()
        self.brickpiece_group = pg.sprite.Group()

        if c.MAP_BRICK in self.map_data:
            for data in self.map_data[c.MAP_BRICK]:
                brick.create_brick(self.brick_group, data, self)

        self.box_group = pg.sprite.Group()
        if c.MAP_BOX in self.map_data:
            for data in self.map_data[c.MAP_BOX]:
                if data["type"] == c.TYPE_COIN:
                    self.box_group.add(
                        box.Box(data["x"], data["y"], data["type"], self.coin_group)
                    )
                else:
                    self.box_group.add(
                        box.Box(data["x"], data["y"], data["type"], self.powerup_group)
                    )

    # Function to set up the player object
    def setup_player(self):
        if self.player is None:
            self.player = player.Player(self.game_info[c.PLAYER_NAME])
        else:
            self.player.restart()
        self.player.rect.x = self.viewport.x + self.player_x
        self.player.rect.bottom = self.player_y
        if c.DEBUG:
            self.player.rect.x = self.viewport.x + c.DEBUG_START_X
            self.player.rect.bottom = c.DEBUG_START_y
        self.viewport.x = self.player.rect.x - 110

    def setup_enemies(self):
        self.enemy_group_list = []
        index = 0
        for data in self.map_data[c.MAP_ENEMY]:
            group = pg.sprite.Group()
            for item in data[str(index)]:
                group.add(enemy.create_enemy(item, self))
            self.enemy_group_list.append(group)
            index += 1

    def setup_checkpoints(self):
        self.checkpoint_group = pg.sprite.Group()
        for data in self.map_data[c.MAP_CHECKPOINT]:
            if c.ENEMY_GROUPID in data:
                enemy_groupid = data[c.ENEMY_GROUPID]
            else:
                enemy_groupid = 0
            if c.MAP_INDEX in data:
                map_index = data[c.MAP_INDEX]
            else:
                map_index = 0
            self.checkpoint_group.add(
                stuff.Checkpoint(
                    data["x"],
                    data["y"],
                    data["width"],
                    data["height"],
                    data["type"],
                    enemy_groupid,
                    map_index,
                )
            )

    def setup_flagpole(self):
        self.flagpole_group = pg.sprite.Group()
        if c.MAP_FLAGPOLE in self.map_data:
            for data in self.map_data[c.MAP_FLAGPOLE]:
                if data["type"] == c.FLAGPOLE_TYPE_FLAG:
                    sprite = stuff.Flag(data["x"], data["y"])
                    self.flag = sprite
                elif data["type"] == c.FLAGPOLE_TYPE_POLE:
                    sprite = stuff.Pole(data["x"], data["y"])
                else:
                    sprite = stuff.PoleTop(data["x"], data["y"])
                self.flagpole_group.add(sprite)

    def setup_sprite_groups(self):
        self.dying_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.shell_group = pg.sprite.Group()

        self.ground_step_pipe_group = pg.sprite.Group(
            self.ground_group, self.pipe_group, self.step_group, self.slider_group
        )
        self.player_group = pg.sprite.Group(self.player)

# RL PART
    def get_relevant_from_group(self, group, entity_type):
        stuffs = []
        for stuff in group:
            dx = stuff.rect.x - self.viewport.x
            if dx < -30 or dx > 790:
                continue
            stuffs.append(
                Entity(
                    x=stuff.rect.centerx + 21 - self.player.rect.centerx,
                    y=stuff.rect.centery + 21 - self.player.rect.bottom,
                    w=stuff.rect.w,
                    h=stuff.rect.h,
                    dx=stuff.x_vel if hasattr(stuff, "x_vel") else 0,
                    dy=stuff.y_vel if hasattr(stuff, "y_vel") else 0,
                    ty=entity_type,
                )
            )
        return stuffs

    def get_relevant_from_large_group(self, group, entity_type=EntityType.GROUND):
        largers = []
        for large in group:
            dlx = large.rect.x - self.viewport.x
            drx = large.rect.x + large.rect.w - self.viewport.x
            if drx < -30 or dlx > 790:
                continue
            for x in range(large.rect.x, large.rect.x + large.rect.w, 43):
                dx = x - self.viewport.x
                if dx < -30:
                    continue
                if dx > 790:
                    break
                for y in range(large.rect.y, large.rect.y + large.rect.h, 43):
                    largers.append(
                        Entity(
                            x=x + 21 - self.player.rect.centerx,
                            y=y + 21 - self.player.rect.bottom,
                            w=43,
                            h=43,
                            dx=0,
                            dy=0,
                            ty=entity_type,
                        )
                    )
            # largers.append(Entity(
            #     x=large.rect.centerx - self.player.rect.centerx,
            #     y=large.rect.centery - self.player.rect.bottom,
            #     w=large.rect.w,
            #     h=large.rect.h,
            #     dx=large.x_vel if hasattr(large, 'x_vel') else 0,
            #     dy=large.y_vel if hasattr(large, 'y_vel') else 0,
            #     ty=entity_type,
            # ))
        return largers

    def get_ground(self):
        return (
            self.get_relevant_from_large_group(self.ground_group)
            + self.get_relevant_from_large_group(self.pipe_group)
            + self.get_relevant_from_large_group(self.step_group)
        )

    def get_enemies(self):
        return self.get_relevant_from_group(
            self.enemy_group, EntityType.ENEMY
        ) + self.get_relevant_from_group(self.shell_group, EntityType.ENEMY)

    def get_state(self):
        # 20x15 grid
        state = [[None] * 20 for _ in range(15)]

        # make sure grid aligns with the entities
        grid_x = (self.viewport.x + 7) // 43 * 43
        grid_y = (self.viewport.y) // 43 * 43

        entities = [
            Entity(
                0,
                0,
                self.player.rect.w,
                self.player.rect.h,
                self.dx,
                self.player.y_vel,
                EntityType.PLAYER,
            )
        ]
        entities += self.get_ground()
        entities += self.get_relevant_from_group(self.brick_group, EntityType.BRICK)
        entities += self.get_relevant_from_group(self.box_group, EntityType.BOX)
        entities += self.get_enemies()
        entities += self.get_relevant_from_group(self.powerup_group, EntityType.POWERUP)

        # put the entities into the state grid
        for entity in entities:
            entity_y = (entity.y + (self.player.rect.bottom - grid_y)) // 43
            entity_x = (entity.x + (self.player.rect.centerx - grid_x)) // 43
            if entity_y < 0 or entity_y >= 15 or entity_x < 0 or entity_x >= 20:
                continue
            state[entity_y][entity_x] = entity

        return state

    def state_to_tensor(self) -> torch.Tensor:
        num_frames = len(self.state_queue)
        height = len(self.state_queue[0])
        width = len(self.state_queue[0][0])
        state_np = np.zeros((num_frames * 7, height, width), dtype=np.float32)

        for i, frame in enumerate(self.state_queue):
            offset = i * 7
            for y, row in enumerate(frame):
                for x, entity in enumerate(row):
                    # If the grid cell has an entity, map its properties to the channels
                    if entity is not None:
                        state_np[offset, y, x] = entity.x / 860.0
                        state_np[offset + 1, y, x] = entity.y / 645.0
                        state_np[offset + 2, y, x] = entity.w / 43.0
                        state_np[offset + 3, y, x] = entity.h / 86.0
                        state_np[offset + 4, y, x] = entity.dx / 20.0
                        state_np[offset + 5, y, x] = entity.dy / 20.0
                        state_np[offset + 6, y, x] = entity.ty.value / 5.0

        np.clip(state_np, -1.0, 1.0, out=state_np)

        return torch.from_numpy(state_np)

    def calc_reward_alex(self, surface, keys, current_time):
        # force longer minimum jump
        if keys[keybinding["jump"]]:
            if self.jumptimer == 0:
                self.jumptimer = 10
        if self.jumptimer > 0:
            keys[keybinding["jump"]] = True
            self.jumptimer -= 1

        self.handle_states(keys)  # do move and update state
        state = self.get_state()  # get RL state
        self.state_queue.append(state)
        while len(self.state_queue) < self.state_queue.maxlen:
            self.state_queue.append(state)

        use_max_x = False
        if use_max_x:
            # change max x here using offset when teleported to beginning
            # self.max_x = ...

            # detect improvement of max x
            improved = False
            if self.player.rect.x > self.max_x:
                improved = True
            if improved: # +r when improving
                self.reward = self.player.rect.x - self.max_x
            else: # -r when not
                self.reward = -0.1

            # # small attraction to the right
            # self.reward += self.player.x_vel * 0.00001

        else: # use dx instead
            # use dx as reward, more to the right: +r, more left -r
            d_x = self.player.rect.x - self.prev_x
            self.prev_x = self.player.rect.x
            self.reward = d_x - 0.1

        # # +r for jumping when standing still
        # if d_x == 0 and self.player.rect.y > self.prev_y:
        #     self.reward += (self.player.rect.y - self.prev_y) * 0.5
        #     print("hier")
        # self.prev_y = self.player.rect.y

        # # use score as well +r when added score
        # d_score = self.game_info[c.SCORE] - self.prev_score
        # self.prev_score = self.game_info[c.SCORE]
        # self.reward += d_score * 0.02

        # print reward trace
        if self.reward == self.prev_reward:
            self.count +=1
            print("                       ", end = "\r")
            print(f"{self.reward} x {self.count}", end = "\r")
        else:
            self.count = 1
            print()
            print(f"{self.reward} x {self.count}", end = "\r")

        # -r when player dies
        if self.player.dead:
            print()
            print("dead")
            self.reward = -15
            print(self.reward)

        self.prev_reward = self.reward # update prev_reward
        self.max_x = max(self.max_x, self.player.rect.x) # update max x

        return self.reward

    def update_alex(self, surface, keys, current_time):
        self.game_info[c.CURRENT_TIME] = self.current_time = current_time
        if self.render:
            self.draw(surface)  # update frame
        reward = self.calc_reward_alex(surface, keys, current_time)

        truncated = False
        if self.player.state != c.FLAGPOLE:
            if self.steps >= 10000 // self.frame_skip:
                truncated = True
                self.player.dead = True
            else:
                self.steps += 1
        else:
            self.player.dead = True

        return self.state_to_tensor(), reward, self.player.dead, truncated

    def reward_pieter(self, dx):
        return ( max(0, (self.player.rect.x - self.best_x) * 0.05)
                 - int(dx <= 0) * 0.01
                 - int(self.player.dead))

    def update_pieter(self, surface, keys, current_time):
        last_x = self.last_x
        for _ in range(self.frame_skip):
            self.handle_states(keys)  # do move and update state
            self.dx = self.player.rect.x - self.last_x
            self.last_x = self.player.rect.x
        state = self.get_state()  # get RL state
        self.state_queue.append(state)
        while len(self.state_queue) < self.state_queue.maxlen:
            self.state_queue.append(state)
        self.game_info[c.CURRENT_TIME] = self.current_time = current_time
        dx = self.player.rect.x - last_x
        reward = self.reward_pieter(dx)
        self.best_x = max(self.best_x, self.player.rect.x)
        if self.render:
            self.draw(surface)  # update frame
            print(reward)
        truncated = False
        if not (self.player.state == c.FLAGPOLE or
                self.player.state == c.WALK_AUTO or
                self.player.state == c.IN_CASTLE):
            if self.steps >= 10000 // self.frame_skip:
                truncated = True
                self.player.dead = True
            else:
                self.steps += 1
        else:
            self.player.dead = True
        return self.state_to_tensor(), reward, self.player.dead, truncated

    def update(self, surface, keys, current_time):
        return self.update_pieter(surface, keys, current_time)
        # return self.update_alex(surface, keys, current_time)

    def handle_states(self, keys):
        self.update_all_sprites(keys)

    def update_all_sprites(self, keys):
        if self.player.dead:
            self.player.update(keys, self.game_info, self.powerup_group)
            if self.current_time - self.death_timer > self.death_timeout:
                self.update_game_info()
                self.done = True
        elif self.player.state == c.IN_CASTLE:
            self.player.update(keys, self.game_info, None)
            self.flagpole_group.update()
            if self.current_time - self.castle_timer > 2000:
                self.update_game_info()
                self.done = True
        elif self.in_frozen_state():
            self.player.update(keys, self.game_info, None)
            self.check_checkpoints()
            self.update_viewport()
            self.overhead_info.update(self.game_info, self.player)
            for score in self.moving_score_list:
                score.update(self.moving_score_list)
        else:
            self.player.update(keys, self.game_info, self.powerup_group)
            self.flagpole_group.update()
            self.check_for_chunk()
            self.check_checkpoints()
            self.slider_group.update()
            self.static_coin_group.update(self.game_info)
            self.enemy_group.update(self.game_info, self)
            self.shell_group.update(self.game_info, self)
            self.brick_group.update()
            self.box_group.update(self.game_info)
            self.powerup_group.update(self.game_info, self)
            self.coin_group.update(self.game_info)
            self.brickpiece_group.update()
            self.dying_group.update(self.game_info, self)
            self.delete_old_sprites()
            self.update_player_position()
            self.check_for_player_death()
            self.update_viewport()
            self.overhead_info.update(self.game_info, self.player)
            for score in self.moving_score_list:
                score.update(self.moving_score_list)

    def check_checkpoints(self):
        checkpoint = pg.sprite.spritecollideany(self.player, self.checkpoint_group)

        if checkpoint:
            if checkpoint.type == c.CHECKPOINT_TYPE_ENEMY:
                index = checkpoint.enemy_groupid #% len(self.enemy_group_list)
                #print('index: ', index)
                group = self.enemy_group_list[index]
                #print('group: ', group)
                self.enemy_group.add(group)
            # TODO: old
            elif checkpoint.type == c.CHECKPOINT_TYPE_FLAG:
                self.player.state = c.FLAGPOLE
                if self.player.rect.bottom < self.flag.rect.y:
                    self.player.rect.bottom = self.flag.rect.y
                self.flag.state = c.SLIDE_DOWN
                self.update_flag_score()
            elif checkpoint.type == c.CHECKPOINT_TYPE_CASTLE:
                self.player.state = c.IN_CASTLE
                self.player.x_vel = 0
                self.castle_timer = self.current_time
                self.flagpole_group.add(stuff.CastleFlag(8745, 322))
            elif (
                checkpoint.type == c.CHECKPOINT_TYPE_MUSHROOM and self.player.y_vel < 0
            ):
                mushroom_box = box.Box(checkpoint.rect.x, checkpoint.rect.bottom - 40,
                                c.TYPE_LIFEMUSHROOM, self.powerup_group)

                mushroom_box.start_bump(self.moving_score_list)
                self.box_group.add(mushroom_box)
                self.player.y_vel = 7
                self.player.rect.y = mushroom_box.rect.bottom
                self.player.state = c.FALL
            # elif checkpoint.type == c.CHECKPOINT_TYPE_PIPE:
            #     self.player.state = c.WALK_AUTO
            elif checkpoint.type == c.CHECKPOINT_TYPE_PIPE_UP:
                self.change_map(checkpoint.map_index, checkpoint.type)
            elif checkpoint.type == c.CHECKPOINT_TYPE_MAP:
                self.change_map(checkpoint.map_index, checkpoint.type)
            # elif checkpoint.type == c.CHECKPOINT_TYPE_BOSS:
            #     self.player.state = c.WALK_AUTO
            checkpoint.kill()

    def update_flag_score(self):
        base_y = c.GROUND_HEIGHT - 80

        y_score_list = [
            (base_y, 100),
            (base_y - 120, 400),
            (base_y - 200, 800),
            (base_y - 320, 2000),
            (0, 5000),
        ]
        for y, score in y_score_list:
            if self.player.rect.y > y:
                self.update_score(score, self.flag)
                break

    def update_player_position(self):
        if self.player.state == c.UP_OUT_PIPE:
            return

        self.player.rect.x += round(self.player.x_vel)
        if self.player.rect.x < self.left_bound:
            self.player.rect.x = self.left_bound

        self.check_player_x_collisions()

        if not self.player.dead:
            self.player.rect.y += round(self.player.y_vel)
            self.check_player_y_collisions()

    def check_player_x_collisions(self):
        ground_step_pipe = pg.sprite.spritecollideany(
            self.player, self.ground_step_pipe_group
        )
        brick = pg.sprite.spritecollideany(self.player, self.brick_group)
        box = pg.sprite.spritecollideany(self.player, self.box_group)
        enemy = pg.sprite.spritecollideany(self.player, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.player, self.shell_group)
        powerup = pg.sprite.spritecollideany(self.player, self.powerup_group)
        coin = pg.sprite.spritecollideany(self.player, self.static_coin_group)

        if box:
            self.adjust_player_for_x_collisions(box)
        elif brick:
            self.adjust_player_for_x_collisions(brick)
        elif ground_step_pipe:
            if (
                ground_step_pipe.name == c.MAP_PIPE
                and ground_step_pipe.type == c.PIPE_TYPE_HORIZONTAL
            ):
                return
            self.adjust_player_for_x_collisions(ground_step_pipe)
        elif powerup:
            if powerup.type == c.TYPE_MUSHROOM:
                self.update_score(1000, powerup, 0)
                if not self.player.big:
                    self.player.y_vel = -1
                    self.player.state = c.SMALL_TO_BIG
            elif powerup.type == c.TYPE_FIREFLOWER:
                self.update_score(1000, powerup, 0)
                if not self.player.big:
                    self.player.state = c.SMALL_TO_BIG
                elif self.player.big and not self.player.fire:
                    self.player.state = c.BIG_TO_FIRE
            elif powerup.type == c.TYPE_STAR:
                self.update_score(1000, powerup, 0)
                self.player.invincible = True
            elif powerup.type == c.TYPE_LIFEMUSHROOM:
                self.update_score(500, powerup, 0)
                self.game_info[c.LIVES] += 1
            if powerup.type != c.TYPE_FIREBALL:
                powerup.kill()
        elif enemy:
            if self.player.invincible:
                self.update_score(100, enemy, 0)
                self.move_to_dying_group(self.enemy_group, enemy)
                direction = c.RIGHT if self.player.facing_right else c.LEFT
                enemy.start_death_jump(direction)
            elif self.player.hurt_invincible:
                pass
            elif self.player.big:
                self.player.y_vel = -1
                self.player.state = c.BIG_TO_SMALL
            else:
                self.player.start_death_jump(self.game_info)
                self.death_timer = self.current_time
        elif shell:
            if shell.state == c.SHELL_SLIDE:
                if self.player.invincible:
                    self.update_score(200, shell, 0)
                    self.move_to_dying_group(self.shell_group, shell)
                    direction = c.RIGHT if self.player.facing_right else c.LEFT
                    shell.start_death_jump(direction)
                elif self.player.hurt_invincible:
                    pass
                elif self.player.big:
                    self.player.y_vel = -1
                    self.player.state = c.BIG_TO_SMALL
                else:
                    self.player.start_death_jump(self.game_info)
                    self.death_timer = self.current_time
            else:
                self.update_score(400, shell, 0)
                if self.player.rect.x < shell.rect.x:
                    self.player.rect.left = shell.rect.x
                    shell.direction = c.RIGHT
                    shell.x_vel = 10
                else:
                    self.player.rect.x = shell.rect.left
                    shell.direction = c.LEFT
                    shell.x_vel = -10
                shell.rect.x += shell.x_vel * 4
                shell.state = c.SHELL_SLIDE
        elif coin:
            self.update_score(100, coin, 1)
            coin.kill()

    def adjust_player_for_x_collisions(self, collider):
        if collider.name == c.MAP_SLIDER:
            return

        if self.player.rect.x < collider.rect.x:
            self.player.rect.right = collider.rect.left
        else:
            self.player.rect.left = collider.rect.right
        self.player.x_vel = 0

    def check_player_y_collisions(self):
        ground_step_pipe = pg.sprite.spritecollideany(
            self.player, self.ground_step_pipe_group
        )
        enemy = pg.sprite.spritecollideany(self.player, self.enemy_group)
        shell = pg.sprite.spritecollideany(self.player, self.shell_group)

        # decrease runtime delay: when player is on the ground, don't check brick and box
        if self.player.rect.bottom < c.GROUND_HEIGHT:
            brick = pg.sprite.spritecollideany(self.player, self.brick_group)
            box = pg.sprite.spritecollideany(self.player, self.box_group)
            brick, box = self.prevent_collision_conflict(brick, box)
        else:
            brick, box = False, False

        if box:
            self.adjust_player_for_y_collisions(box)
        elif brick:
            self.adjust_player_for_y_collisions(brick)
        elif ground_step_pipe:
            self.adjust_player_for_y_collisions(ground_step_pipe)
        elif enemy:
            if self.player.invincible:
                self.update_score(100, enemy, 0)
                self.move_to_dying_group(self.enemy_group, enemy)
                direction = c.RIGHT if self.player.facing_right else c.LEFT
                enemy.start_death_jump(direction)
            elif (
                enemy.name == c.PIRANHA
                or enemy.name == c.FIRESTICK
                or enemy.name == c.FIRE_KOOPA
                or enemy.name == c.FIRE
            ):
                pass
            elif self.player.y_vel > 0:
                self.update_score(100, enemy, 0)
                enemy.state = c.JUMPED_ON
                if enemy.name == c.GOOMBA:
                    self.move_to_dying_group(self.enemy_group, enemy)
                elif enemy.name == c.KOOPA or enemy.name == c.FLY_KOOPA:
                    self.enemy_group.remove(enemy)
                    self.shell_group.add(enemy)

                self.player.rect.bottom = enemy.rect.top
                self.player.state = c.JUMP
                self.player.y_vel = -7
        elif shell:
            if self.player.y_vel > 0:
                if shell.state != c.SHELL_SLIDE:
                    shell.state = c.SHELL_SLIDE
                    if self.player.rect.centerx < shell.rect.centerx:
                        shell.direction = c.RIGHT
                        shell.rect.left = self.player.rect.right + 5
                    else:
                        shell.direction = c.LEFT
                        shell.rect.right = self.player.rect.left - 5
        self.check_is_falling(self.player)
        self.check_if_player_on_IN_pipe()

    def prevent_collision_conflict(self, sprite1, sprite2):
        if sprite1 and sprite2:
            distance1 = abs(self.player.rect.centerx - sprite1.rect.centerx)
            distance2 = abs(self.player.rect.centerx - sprite2.rect.centerx)
            if distance1 < distance2:
                sprite2 = False
            else:
                sprite1 = False
        return sprite1, sprite2

    def adjust_player_for_y_collisions(self, sprite):
        if self.player.rect.top > sprite.rect.top:
            if sprite.name == c.MAP_BRICK:
                self.check_if_enemy_on_brick_box(sprite)
                if sprite.state == c.RESTING:
                    if self.player.big and sprite.type == c.TYPE_NONE:
                        sprite.change_to_piece(self.dying_group)
                    else:
                        if sprite.type == c.TYPE_COIN:
                            self.update_score(200, sprite, 1)
                        sprite.start_bump(self.moving_score_list)
            elif sprite.name == c.MAP_BOX:
                self.check_if_enemy_on_brick_box(sprite)
                if sprite.state == c.RESTING:
                    if sprite.type == c.TYPE_COIN:
                        self.update_score(200, sprite, 1)
                    sprite.start_bump(self.moving_score_list)
            elif sprite.name == c.MAP_PIPE and sprite.type == c.PIPE_TYPE_HORIZONTAL:
                return

            self.player.y_vel = 7
            self.player.rect.top = sprite.rect.bottom
            self.player.state = c.FALL
        else:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            if self.player.state == c.FLAGPOLE:
                self.player.state = c.WALK_AUTO
            elif self.player.state == c.END_OF_LEVEL_FALL:
                self.player.state = c.WALK_AUTO
            else:
                self.player.state = c.WALK

    def check_if_enemy_on_brick_box(self, brick):
        brick.rect.y -= 5
        enemy = pg.sprite.spritecollideany(brick, self.enemy_group)
        if enemy:
            self.update_score(100, enemy, 0)
            self.move_to_dying_group(self.enemy_group, enemy)
            if self.player.rect.centerx > brick.rect.centerx:
                direction = c.RIGHT
            else:
                direction = c.LEFT
            enemy.start_death_jump(direction)
        brick.rect.y += 5

    def in_frozen_state(self):
        if (
            self.player.state == c.SMALL_TO_BIG
            or self.player.state == c.BIG_TO_SMALL
            or self.player.state == c.BIG_TO_FIRE
            or self.player.state == c.DEATH_JUMP
            or self.player.state == c.DOWN_TO_PIPE
            or self.player.state == c.UP_OUT_PIPE
        ):
            return True
        else:
            return False

    def check_is_falling(self, sprite):
        sprite.rect.y += 1
        check_group = pg.sprite.Group(
            self.ground_step_pipe_group, self.brick_group, self.box_group
        )
        if pg.sprite.spritecollideany(sprite, check_group) is None:
            if sprite.state == c.WALK_AUTO or sprite.state == c.END_OF_LEVEL_FALL:
                sprite.state = c.END_OF_LEVEL_FALL
            elif (
                sprite.state != c.JUMP
                and sprite.state != c.FLAGPOLE
                and not self.in_frozen_state()
            ):
                sprite.state = c.FALL
        sprite.rect.y -= 1

    def check_for_player_death(self):
        if self.player.rect.y > c.SCREEN_HEIGHT or self.overhead_info.time <= 0:
            self.player.start_death_jump(self.game_info)
            self.death_timer = self.current_time

    def check_if_player_on_IN_pipe(self):
        """check if player is on the pipe which can go down in to it"""
        self.player.rect.y += 1
        pipe = pg.sprite.spritecollideany(self.player, self.pipe_group)
        if pipe and pipe.type == c.PIPE_TYPE_IN:
            if (
                self.player.crouching
                and self.player.rect.x < pipe.rect.centerx
                and self.player.rect.right > pipe.rect.centerx
            ):
                self.player.state = c.DOWN_TO_PIPE
        self.player.rect.y -= 1

    def update_game_info(self):
        if self.player.dead:
            self.reset = True
            self.persist[c.LIVES] -= 1

        if self.persist[c.LIVES] == 0:
            self.next = c.GAME_OVER
        # elif self.overhead_info.time == 0:
        #     self.next = c.TIME_OUT
        elif self.player.dead:
            self.next = c.LOAD_SCREEN
        else:
            self.next = c.LEVEL
            # self.game_info[c.LEVEL_NUM] += 1
            # self.next = c.LOAD_SCREEN

    def update_viewport(self):
        third = self.viewport.x + self.viewport.w // 3
        player_center = self.player.rect.centerx

        if (
            self.player.state != c.SMALL_TO_BIG
            and self.player.state != c.BIG_TO_FIRE
            and self.player.state != c.BIG_TO_SMALL
        ):
            if (self.player.x_vel > 0 and player_center >= third):
                self.viewport.x += round(self.player.x_vel)
            elif self.player.x_vel < 0 and self.viewport.x > self.left_bound:
                self.viewport.x += round(self.player.x_vel)

        self.left_bound = max(self.left_bound, self.viewport.x - 100)

    def move_to_dying_group(self, group, sprite):
        group.remove(sprite)
        self.dying_group.add(sprite)

    def update_score(self, score, sprite, coin_num=0):
        self.game_info[c.SCORE] += score
        self.game_info[c.COIN_TOTAL] += coin_num
        x = sprite.rect.x
        y = sprite.rect.y - 10
        self.moving_score_list.append(stuff.Score(x, y, score))

    def draw(self, surface):
        #self.level.blit(self.background, self.viewport, self.viewport)
        # Repeat the background image infinitely
        bg_width = self.background.get_width()
        rel_x = (self.bg_offset + self.viewport.x) % bg_width

        self.level.blit(self.background, (int(self.viewport.x - rel_x), 0))
        self.level.blit(self.background, (int(self.viewport.x - rel_x + bg_width), 0))

        #for x in range(0, self.level.get_width(), bg_width):
        #    self.level.blit(self.background, (x, 0))

        self.ground_group.draw(self.level)
        self.ground_step_pipe_group.draw(self.level)
        self.powerup_group.draw(self.level)
        self.brick_group.draw(self.level)
        self.box_group.draw(self.level)
        self.coin_group.draw(self.level)
        self.dying_group.draw(self.level)
        self.brickpiece_group.draw(self.level)
        self.flagpole_group.draw(self.level)
        self.shell_group.draw(self.level)
        self.enemy_group.draw(self.level)
        self.player_group.draw(self.level)
        self.static_coin_group.draw(self.level)
        self.slider_group.draw(self.level)
        self.pipe_group.draw(self.level)
        for score in self.moving_score_list:
            score.draw(self.level)
        if c.DEBUG:
            self.ground_step_pipe_group.draw(self.level)
            self.checkpoint_group.draw(self.level)

        surface.blit(self.level, (0, 0), self.viewport)
        self.overhead_info.draw(surface)
