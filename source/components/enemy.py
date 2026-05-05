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

import math
import pygame as pg
from .. import setup, tools
from .. import constants as c

# Speed of the enemies
ENEMY_SPEED = 1

# Function to create different types of enemies based on the input parameters
def create_enemy(item, level):
    # Extracting relevant information from the item dictionary
    dir = c.LEFT if item['direction'] == 0 else c.RIGHT
    color = item[c.COLOR]
    if c.ENEMY_RANGE in item:
        in_range = item[c.ENEMY_RANGE]
        range_start = item['range_start']
        range_end = item['range_end']
    else:
        in_range = False
        range_start = range_end = 0

    # Creating different enemy types based on the 'type' key in the item dictionary
    if item['type'] == c.ENEMY_TYPE_GOOMBA:
        sprite = Goomba(item['x'], item['y'], dir, color,
            in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_KOOPA:
        sprite = Koopa(item['x'], item['y'], dir, color,
            in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_FLY_KOOPA:
        isVertical = False if item['is_vertical'] == 0 else True
        sprite = FlyKoopa(item['x'], item['y'], dir, color,
            in_range, range_start, range_end, isVertical)
    elif item['type'] == c.ENEMY_TYPE_PIRANHA:
        sprite = Piranha(item['x'], item['y'], dir, color,
            in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_FIRE_KOOPA:
        sprite = FireKoopa(item['x'], item['y'], dir, color,
            in_range, range_start, range_end, level)
    elif item['type'] == c.ENEMY_TYPE_FIRESTICK:
        '''use a number of fireballs to stimulate a firestick'''
        sprite = []
        num = item['num']
        center_x, center_y = item['x'], item['y']
        for i in range(num):
            radius = i * 21 # 8 * 2.69 = 21
            sprite.append(FireStick(center_x, center_y, dir, color,
                radius))
    return sprite

# Base class for all enemies
class Enemy(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

    # Setting up the enemy's initial properties
    def setup_enemy(self, x, y, direction, name, sheet, frame_rect_list,
                        in_range, range_start, range_end, isVertical=False):
        self.frames = []
        self.frame_index = 0
        self.animate_timer = 0
        self.gravity = 1.5
        self.state = c.WALK

        self.name = name
        self.direction = direction
        self.load_frames(sheet, frame_rect_list)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.in_range = in_range
        self.range_start = range_start
        self.range_end = range_end
        self.isVertical = isVertical
        self.set_velocity()
        self.death_timer = 0

    # Loading sprite frames from a sprite sheet
    def load_frames(self, sheet, frame_rect_list):
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect, 
                            c.BLACK, c.SIZE_MULTIPLIER))

    # Setting the initial velocity of the enemy
    def set_velocity(self):
        if self.isVertical:
            self.x_vel = 0
            self.y_vel = ENEMY_SPEED
        else:
            self.x_vel = ENEMY_SPEED *-1 if self.direction == c.LEFT else ENEMY_SPEED
            self.y_vel = 0

    # Updating the enemy's position and state
    def update(self, game_info, level):
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state()
        self.animation()
        self.update_position(level)

    # Handling the different states of the enemy
    def handle_state(self):
        if (self.state == c.WALK or
            self.state == c.FLY):
            self.walking()
        elif self.state == c.FALL:
            self.falling()
        elif self.state == c.JUMPED_ON:
            self.jumped_on()
        elif self.state == c.DEATH_JUMP:
            self.death_jumping()
        elif self.state == c.SHELL_SLIDE:
            self.shell_sliding()
        elif self.state == c.REVEAL:
            self.revealing()

    # Handling the walking animation state
    def walking(self):
        if (self.current_time - self.animate_timer) > 125:
            if self.direction == c.RIGHT:
                if self.frame_index == 4:
                    self.frame_index += 1
                elif self.frame_index == 5:
                    self.frame_index = 4
            else:
                if self.frame_index == 0:
                    self.frame_index += 1
                elif self.frame_index == 1:
                    self.frame_index = 0
            self.animate_timer = self.current_time

    # Handling the falling animation state
    def falling(self):
        if self.y_vel < 10:
            self.y_vel += self.gravity

    # Handling the jumped on animation state (when the enemy is jumped on by the player)
    def jumped_on(self):
        pass

    # Handling the death jumping animation state (when the enemy is killed)
    def death_jumping(self):
        self.rect.y += self.y_vel
        self.rect.x += self.x_vel
        self.y_vel += self.gravity
        if self.rect.y > c.SCREEN_HEIGHT:
            self.kill()

    # Handling the shell sliding animation state (when the enemy is in shell form and slides)
    def shell_sliding(self):
        if self.direction == c.RIGHT:
            self.x_vel = 10
        else:
            self.x_vel = -10

    # Handling the revealing animation state (when the enemy is revealed)
    def revealing(self):
        pass

    # Starting the death jump animation state (when the enemy is killed and jumps)
    def start_death_jump(self, direction):
        self.y_vel = -8
        self.x_vel = 2 if direction == c.RIGHT else -2
        self.gravity = .5
        self.frame_index = 3
        self.state = c.DEATH_JUMP

    # Updating the enemy's animation
    def animation(self):
        self.image = self.frames[self.frame_index]

    # Updating the enemy's position
    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)

        if self.in_range and self.isVertical:
            if self.rect.y < self.range_start:
                self.rect.y = self.range_start
                self.y_vel = ENEMY_SPEED
            elif self.rect.bottom > self.range_end:
                self.rect.bottom = self.range_end
                self.y_vel = -1 * ENEMY_SPEED

        self.rect.y += self.y_vel
        if (self.state != c.DEATH_JUMP and 
            self.state != c.FLY):
            self.check_y_collisions(level)

        if self.rect.x <= 0:
            self.kill()
        elif self.rect.y > (level.viewport.bottom):
            self.kill()

    # Checking for collisions in the x-direction
    def check_x_collisions(self, level):
        if self.in_range and not self.isVertical:
            if self.rect.x < self.range_start:
                self.rect.x = self.range_start
                self.change_direction(c.RIGHT)
            elif self.rect.right > self.range_end:
                self.rect.right = self.range_end
                self.change_direction(c.LEFT)
        else:
            collider = pg.sprite.spritecollideany(self, level.ground_step_pipe_group)
            if collider:
                if self.direction == c.RIGHT:
                    self.rect.right = collider.rect.left
                    self.change_direction(c.LEFT)
                elif self.direction == c.LEFT:
                    self.rect.left = collider.rect.right
                    self.change_direction(c.RIGHT)
            if (self.state != c.SHELL_SLIDE and
                self.state != c.DEATH_JUMP and
                self.state != c.JUMPED_ON):
                collider = pg.sprite.spritecollideany(self, pg.sprite.Group(level.enemy_group))
                if collider and collider is not self:
                    if self.direction == c.RIGHT:
                        tmp = self.rect.right
                        self.rect.right = collider.rect.left
                        collider.rect.left = tmp
                        collider.change_direction(c.RIGHT)
                        self.change_direction(c.LEFT)
                    elif self.direction == c.LEFT:
                        tmp = self.rect.left
                        self.rect.left = collider.rect.right
                        collider.rect.right = tmp
                        collider.change_direction(c.LEFT)
                        self.change_direction(c.RIGHT)

        if self.state == c.SHELL_SLIDE:
            enemy = pg.sprite.spritecollideany(self, level.enemy_group)
            if enemy:
                level.update_score(100, enemy, 0)
                level.move_to_dying_group(level.enemy_group, enemy)
                enemy.start_death_jump(self.direction)

    # Changing the enemy's direction (left or right)
    def change_direction(self, direction):
        self.direction = direction
        if self.direction == c.RIGHT:
            self.x_vel = ENEMY_SPEED
            if self.state == c.WALK or self.state == c.FLY:
                self.frame_index = 4
        else:
            self.x_vel = ENEMY_SPEED * -1
            if self.state == c.WALK or self.state == c.FLY:
                self.frame_index = 0

    # Checking for collisions in the y-direction
    def check_y_collisions(self, level):
        # decrease runtime delay: when enemy is on the ground, don't check brick and box
        if self.rect.bottom >= c.GROUND_HEIGHT:
            sprite_group = level.ground_step_pipe_group
        else:
            sprite_group = pg.sprite.Group(level.ground_step_pipe_group,
                            level.brick_group, level.box_group, level.enemy_group, level.powerup_group)
        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite and sprite is not self and sprite.name != c.MAP_SLIDER:
            if self.rect.top <= sprite.rect.top:
                self.rect.bottom = sprite.rect.y
                self.y_vel = 0
                self.state = c.WALK
        level.check_is_falling(self)

# Class representing the Goomba enemy
class Goomba(Enemy):
    def __init__(self, x, y, direction, color, in_range,
                range_start, range_end, name=c.GOOMBA):
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET],
                    frame_rect_list, in_range, range_start, range_end)
        # dead jump image
        self.frames.append(pg.transform.flip(self.frames[2], False, True))
        # right walk images
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))

    # Getting the frame rectangles for the Goomba based on its color
    def get_frame_rect(self, color):
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(0, 34, 16, 16), (30, 34, 16, 16), 
                        (61, 30, 16, 16)]
        else:
            frame_rect_list = [(0, 4, 16, 16), (30, 4, 16, 16), 
                        (61, 0, 16, 16)]
        return frame_rect_list

    # Handling the jumped on animation state for the Goomba
    def jumped_on(self):
        self.x_vel = 0
        self.frame_index = 2
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif (self.current_time - self.death_timer) > 500:
            self.kill()

# Class representing the Koopa enemy
class Koopa(Enemy):
    def __init__(self, x, y, direction, color, in_range,
                range_start, range_end, name=c.KOOPA):
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET],
                    frame_rect_list, in_range, range_start, range_end)
        # dead jump image
        self.frames.append(pg.transform.flip(self.frames[2], False, True))
        # right walk images
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))

    # Getting the frame rectangles for the Koopa based on its color
    def get_frame_rect(self, color):
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(150, 0, 16, 24), (180, 0, 16, 24),
                        (360, 5, 16, 15)]
        elif color == c.COLOR_TYPE_RED:
            frame_rect_list = [(150, 30, 16, 24), (180, 30, 16, 24),
                        (360, 35, 16, 15)]
        else:
            frame_rect_list = [(150, 60, 16, 24), (180, 60, 16, 24),
                        (360, 65, 16, 15)]
        return frame_rect_list

    # Handling the jumped on animation state for the Koopa
    def jumped_on(self):
        self.x_vel = 0
        self.frame_index = 2
        x = self.rect.x
        bottom = self.rect.bottom
        self.rect = self.frames[self.frame_index].get_rect()
        self.rect.x = x
        self.rect.bottom = bottom
        self.in_range = False

# Class representing the Flying Koopa enemy
class FlyKoopa(Enemy):
    def __init__(self, x, y, direction, color, in_range, 
                range_start, range_end, isVertical, name=c.FLY_KOOPA):
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET], 
                    frame_rect_list, in_range, range_start, range_end, isVertical)
        # dead jump image
        self.frames.append(pg.transform.flip(self.frames[2], False, True))
        # right walk images
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))
        self.state = c.FLY

    # Getting the frame rectangles for the Flying Koopa based on its color
    def get_frame_rect(self, color):
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(90, 0, 16, 24), (120, 0, 16, 24), 
                        (330, 5, 16, 15)]
        else:
            frame_rect_list = [(90, 30, 16, 24), (120, 30, 16, 24), 
                        (330, 35, 16, 15)]
        return frame_rect_list

    # Handling the jumped on animation state for the Flying Koopa
    def jumped_on(self):
        self.x_vel = 0
        self.frame_index = 2
        x = self.rect.x
        bottom = self.rect.bottom
        self.rect = self.frames[self.frame_index].get_rect()
        self.rect.x = x
        self.rect.bottom = bottom
        self.in_range = False
        self.isVertical = False

# Class representing the Fire Koopa enemy
class FireKoopa(Enemy):
    def __init__(self, x, y, direction, color, in_range,
                range_start, range_end, level, name=c.FIRE_KOOPA):
        Enemy.__init__(self)
        frame_rect_list = [(2, 210, 32, 32), (42, 210, 32, 32),
                            (82, 210, 32, 32), (122, 210, 32, 32)]
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET], 
                    frame_rect_list, in_range, range_start, range_end)
        # right walk images
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))
        self.frames.append(pg.transform.flip(self.frames[2], True, False))
        self.frames.append(pg.transform.flip(self.frames[3], True, False))
        self.x_vel = 0
        self.gravity = 0.3
        self.level = level
        self.fire_timer = 0
        self.jump_timer = 0

    def load_frames(self, sheet, frame_rect_list):
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect,
                            c.BLACK, c.BRICK_SIZE_MULTIPLIER))

    def walking(self):
        if (self.current_time - self.animate_timer) > 250:
            if self.direction == c.RIGHT:
                self.frame_index += 1
                if self.frame_index > 7:
                    self.frame_index = 4
            else:
                self.frame_index += 1
                if self.frame_index > 3:
                    self.frame_index = 0
            self.animate_timer = self.current_time

        self.shoot_fire()
        if self.should_jump():
            self.y_vel = -7

    def falling(self):
        if self.y_vel < 7:
            self.y_vel += self.gravity
        self.shoot_fire()

    def should_jump(self):
        if (self.rect.x - self.level.player.rect.x) < 400:
            if (self.current_time - self.jump_timer) > 2500:
                self.jump_timer = self.current_time
                return True
        return False

    def shoot_fire(self):
        if (self.current_time - self.fire_timer) > 3000:
            self.fire_timer = self.current_time
            self.level.enemy_group.add(Fire(self.rect.x, self.rect.bottom-20, self.direction))

# Class representing the Fire projectile
class Fire(Enemy):
    def __init__(self, x, y, direction, name=c.FIRE):
        Enemy.__init__(self)
        frame_rect_list = [(101, 253, 23, 8), (131, 253, 23, 8)]
        in_range, range_start, range_end = False, 0, 0
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET], 
                    frame_rect_list, in_range, range_start, range_end)
        # right images
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))
        self.state = c.FLY
        self.x_vel = 5 if self.direction == c.RIGHT else -5

    # Checking for collisions in the x-direction for the Fire projectile
    def check_x_collisions(self, level):
        sprite_group = pg.sprite.Group(level.ground_step_pipe_group,
                            level.brick_group, level.box_group)
        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite:
            self.kill()

    def start_death_jump(self, direction):
        self.kill()

# Class representing the Piranha enemy
class Piranha(Enemy):
    def __init__(self, x, y, direction, color, in_range, 
                range_start, range_end, name=c.PIRANHA):
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET], 
                    frame_rect_list, in_range, range_start, range_end)
        self.state = c.REVEAL
        self.y_vel = 1
        self.wait_timer = 0
        self.group = pg.sprite.Group()
        self.group.add(self)
        
    # Getting the frame rectangles for the Piranha based on its color
    def get_frame_rect(self, color):
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(390, 30, 16, 24), (420, 30, 16, 24)]
        else:
            frame_rect_list = [(390, 60, 16, 24), (420, 60, 16, 24)]
        return frame_rect_list

    def revealing(self):
        if (self.current_time - self.animate_timer) > 250:
            if self.frame_index == 0:
                self.frame_index += 1
            elif self.frame_index == 1:
                self.frame_index = 0
            self.animate_timer = self.current_time

    def update_position(self, level):
        if self.check_player_is_on(level):
            pass
        else:
            if self.rect.y < self.range_start:
                self.rect.y = self.range_start
                self.y_vel = 1
            elif self.rect.bottom > self.range_end:
                if self.wait_timer == 0:
                    self.wait_timer = self.current_time
                elif (self.current_time - self.wait_timer) < 3000:
                    return
                else:
                    self.wait_timer = 0
                    self.rect.bottom = self.range_end
                    self.y_vel = -1
            self.rect.y += self.y_vel

    def check_player_is_on(self, level):
        result = False
        self.rect.y -= 5
        sprite = pg.sprite.spritecollideany(self, level.ground_step_pipe_group)
        if sprite:
            if sprite.name == c.MAP_SLIDER:
                self.rect.y += 5
                return False
            else:
                self.rect.y += 5
                return True
        self.rect.y += 5
        return False

# Class representing the FireStick enemy
class FireStick(pg.sprite.Sprite):
    def __init__(self, x, y, direction, color, radius, name=c.FIRESTICK):
        pg.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        self.animate_timer = 0
        self.name = name
        self.direction = direction
        self.load_images()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.radius = radius

    def load_images(self):
        sheet = setup.GFX[c.ENEMY_SHEET]
        self.frames.append(tools.get_image(sheet, 390, 90, 8, 8, 
                        c.BLACK, c.SIZE_MULTIPLIER))
        self.frames.append(tools.get_image(sheet, 398, 90, 8, 8, 
                        c.BLACK, c.SIZE_MULTIPLIER))

    def animation(self):
        if (self.current_time - self.animate_timer) > 250:
            if self.frame_index == 0:
                self.frame_index = 1
            else:
                self.frame_index = 0
            self.animate_timer = self.current_time
        self.image = self.frames[self.frame_index]

    def update(self, game_info):
        self.current_time = game_info[c.CURRENT_TIME]
        self.animation()
        self.update_position()

    def update_position(self):
        angle = math.radians(self.frame_index * 45)
        self.rect.x = self.rect.x + self.radius * math.cos(angle)
        self.rect.y = self.rect.y - self.radius * math.sin(angle)
