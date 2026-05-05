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

import pygame as pg
from .. import setup, tools
from .. import constants as c
from . import stuff

class Powerup(stuff.Stuff):
    """
    Base class for all power-ups.
    """

    def __init__(self, x, y, sheet, image_rect_list, scale):
        """
        Initialize a power-up object.

        Args:
            x (int): The x-coordinate of the power-up's initial position.
            y (int): The y-coordinate of the power-up's initial position.
            sheet (pygame.Surface): The sprite sheet containing the power-up's images.
            image_rect_list (list): List of image rectangles (x, y, width, height) for animation frames.
            scale (int): Scale factor for resizing the power-up's images.
        """
        # Call the parent class constructor
        stuff.Stuff.__init__(self, x, y, sheet, image_rect_list, scale)

        self.rect.centerx = x
        self.state = c.REVEAL
        self.y_vel = -1
        self.x_vel = 0
        self.direction = c.RIGHT
        self.box_height = y
        self.gravity = 1
        self.max_y_vel = 8
        self.animate_timer = 0

    def update_position(self, level):
        """
        Update the power-up's position based on velocity and handle collisions.

        Args:
            level (Level): The current level object.
        """
        self.rect.x += self.x_vel
        self.check_x_collisions(level)

        self.rect.y += self.y_vel
        self.check_y_collisions(level)

        if self.rect.x <= 0:
            self.kill()
        elif self.rect.y > (level.viewport.bottom):
            self.kill()
    
    def change_direction(self, direction):
        self.direction = direction
        if self.direction == c.RIGHT:
            self.x_vel = self.speed
            if self.state == c.WALK or self.state == c.FLY:
                self.frame_index = 4
        else:
            self.x_vel = self.speed * -1
            if self.state == c.WALK or self.state == c.FLY:
                self.frame_index = 0

    def check_x_collisions(self, level):
        """
        Check for collisions with the x-axis (horizontal) and adjust velocity and direction if needed.

        Args:
            level (Level): The current level object.
        """
        sprite_group = pg.sprite.Group(
            level.ground_step_pipe_group, level.brick_group, level.box_group
        )
        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite:
            if self.direction == c.RIGHT:
                self.rect.right = sprite.rect.left - 1
                self.direction = c.LEFT
            elif self.direction == c.LEFT:
                self.rect.left = sprite.rect.right
                self.direction = c.RIGHT
            self.x_vel = self.speed if self.direction == c.RIGHT else -1 * self.speed
            if sprite.name == c.MAP_BRICK:
                self.x_vel = 0
        collider = pg.sprite.spritecollideany(self, pg.sprite.Group(level.powerup_group))
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

    def check_y_collisions(self, level):
        """
        Check for collisions with the y-axis (vertical) and adjust velocity and state if needed.

        Args:
            level (Level): The current level object.
        """
        sprite_group = pg.sprite.Group(
            level.ground_step_pipe_group, level.brick_group, level.box_group, level.powerup_group
        )

        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite and sprite is not self:
            self.y_vel = 0
            self.rect.bottom = sprite.rect.top
            self.state = c.SLIDE
        level.check_is_falling(self)

    def animation(self):
        """Animate the power-up using frames."""
        self.image = self.frames[self.frame_index]


class Mushroom(Powerup):
    """
    Class representing a Mushroom power-up.
    """

    def __init__(self, x, y):
        """
        Initialize a Mushroom power-up object.

        Args:
            x (int): The x-coordinate of the Mushroom's initial position.
            y (int): The y-coordinate of the Mushroom's initial position.
        """
        # Call the parent class constructor
        Powerup.__init__(
            self,
            x,
            y,
            setup.GFX[c.ITEM_SHEET],
            [(0, 0, 16, 16)],
            c.SIZE_MULTIPLIER,
        )
        self.type = c.TYPE_MUSHROOM
        self.speed = 2

    def update(self, game_info, level):
        """
        Update the Mushroom power-up's behavior.

        Args:
            game_info (dict): A dictionary containing game information.
            level (Level): The current level object.
        """
        if self.state == c.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom <= self.box_height:
                self.rect.bottom = self.box_height
                self.y_vel = 0
                self.state = c.SLIDE
        elif self.state == c.SLIDE:
            self.x_vel = self.speed if self.direction == c.RIGHT else -1 * self.speed
        elif self.state == c.FALL:
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity

        if self.state == c.SLIDE or self.state == c.FALL:
            self.update_position(level)
        self.animation()


class LifeMushroom(Mushroom):
    """
    Class representing a Life Mushroom power-up.
    """

    def __init__(self, x, y):
        """
        Initialize a Life Mushroom power-up object.

        Args:
            x (int): The x-coordinate of the Life Mushroom's initial position.
            y (int): The y-coordinate of the Life Mushroom's initial position.
        """
        # Call the parent class constructor
        Mushroom.__init__(
            self,
            x,
            y,
        )
        self.type = c.TYPE_LIFEMUSHROOM
        self.speed = 2


class FireFlower(Powerup):
    """
    Class representing a Fire Flower power-up.
    """

    def __init__(self, x, y):
        """
        Initialize a Fire Flower power-up object.

        Args:
            x (int): The x-coordinate of the Fire Flower's initial position.
            y (int): The y-coordinate of the Fire Flower's initial position.
        """
        frame_rect_list = [(0, 32, 16, 16), (16, 32, 16, 16),
                           (32, 32, 16, 16), (48, 32, 16, 16)]
        # Call the parent class constructor
        Powerup.__init__(
            self,
            x,
            y,
            setup.GFX[c.ITEM_SHEET],
            frame_rect_list,
            c.SIZE_MULTIPLIER,
        )
        self.type = c.TYPE_FIREFLOWER

    def update(self, game_info, *args):
        """
        Update the Fire Flower power-up's behavior.

        Args:
            game_info (dict): A dictionary containing game information.
            *args: Additional arguments (not used in this context).
        """
        self.current_time = game_info[c.CURRENT_TIME]
        if self.state == c.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom <= self.box_height:
                self.rect.bottom = self.box_height
                self.y_vel = 0
                self.state = c.RESTING

        if (self.current_time - self.animate_timer) > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animate_timer = self.current_time

        self.animation()


class Star(Powerup):
    """
    Class representing a Star power-up.
    """

    def __init__(self, x, y):
        """
        Initialize a Star power-up object.

        Args:
            x (int): The x-coordinate of the Star's initial position.
            y (int): The y-coordinate of the Star's initial position.
        """
        frame_rect_list = [(1, 48, 15, 16), (17, 48, 15, 16),
                           (33, 48, 15, 16), (49, 48, 15, 16)]
        # Call the parent class constructor
        Powerup.__init__(
            self,
            x,
            y,
            setup.GFX[c.ITEM_SHEET],
            frame_rect_list,
            c.SIZE_MULTIPLIER,
        )
        self.type = c.TYPE_STAR
        self.gravity = 0.4
        self.speed = 5

    def update(self, game_info, level):
        """
        Update the Star power-up's behavior.

        Args:
            game_info (dict): A dictionary containing game information.
            level (Level): The current level object.
        """
        self.current_time = game_info[c.CURRENT_TIME]
        if self.state == c.REVEAL:
            self.rect.y += self.y_vel
            if self.rect.bottom <= self.box_height:
                self.rect.bottom = self.box_height
                self.y_vel = -2
                self.state = c.BOUNCING
        elif self.state == c.BOUNCING:
            self.y_vel += self.gravity
            self.x_vel = self.speed if self.direction == c.RIGHT else -1 * self.speed

        if (self.current_time - self.animate_timer) > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animate_timer = self.current_time

        if self.state == c.BOUNCING:
            self.update_position(level)
        self.animation()

    def check_y_collisions(self, level):
        """
        Check for collisions with the y-axis (vertical) and adjust velocity if needed.

        Args:
            level (Level): The current level object.
        """
        sprite_group = pg.sprite.Group(
            level.ground_step_pipe_group, level.brick_group, level.box_group
        )

        sprite = pg.sprite.spritecollideany(self, sprite_group)

        if sprite:
            if self.rect.top > sprite.rect.top:
                self.y_vel = 5
            else:
                self.rect.bottom = sprite.rect.y
                self.y_vel = -5


class FireBall(Powerup):
    """
    Class representing a Fire Ball power-up.
    """

    def __init__(self, x, y, facing_right):
        """
        Initialize a Fire Ball power-up object.

        Args:
            x (int): The x-coordinate of the Fire Ball's initial position.
            y (int): The y-coordinate of the Fire Ball's initial position.
            facing_right (bool): Flag indicating whether the Fire Ball is facing right (True) or left (False).
        """
        # first 3 Frames are flying, last 4 frames are exploding
        frame_rect_list = [(96, 144, 8, 8), (104, 144, 8, 8),
                           (96, 152, 8, 8), (104, 152, 8, 8),
                           (112, 144, 16, 16), (112, 160, 16, 16),
                           (112, 176, 16, 16)]
        # Call the parent class constructor
        Powerup.__init__(
            self,
            x,
            y,
            setup.GFX[c.ITEM_SHEET],
            frame_rect_list,
            c.SIZE_MULTIPLIER,
        )
        self.type = c.TYPE_FIREBALL
        self.y_vel = 10
        self.gravity = 0.9
        self.state = c.FLYING
        self.rect.right = x
        if facing_right:
            self.direction = c.RIGHT
            self.x_vel = 12
        else:
            self.direction = c.LEFT
            self.x_vel = -12

    def update(self, game_info, level):
        """
        Update the Fire Ball power-up's behavior.

        Args:
            game_info (dict): A dictionary containing game information.
            level (Level): The current level object.
        """
        self.current_time = game_info[c.CURRENT_TIME]

        if self.state == c.FLYING or self.state == c.BOUNCING:
            self.y_vel += self.gravity
            if (self.current_time - self.animate_timer) > 200:
                if self.frame_index < 3:
                    self.frame_index += 1
                else:
                    self.frame_index = 0
                self.animate_timer = self.current_time
            self.update_position(level)
        elif self.state == c.EXPLODING:
            if (self.current_time - self.animate_timer) > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                else:
                    self.kill()
                self.animate_timer = self.current_time

        self.animation()

    def check_x_collisions(self, level):
        """
        Check for collisions with the x-axis (horizontal) and change state to explode if needed.

        Args:
            level (Level): The current level object.
        """
        sprite_group = pg.sprite.Group(
            level.ground_step_pipe_group, level.brick_group, level.box_group
        )
        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite:
            self.change_to_explode()

    def check_y_collisions(self, level):
        """
        Check for collisions with the y-axis (vertical) and handle collisions with the level and enemies.

        Args:
            level (Level): The current level object.
        """
        sprite_group = pg.sprite.Group(
            level.ground_step_pipe_group, level.brick_group, level.box_group
        )

        sprite = pg.sprite.spritecollideany(self, sprite_group)
        enemy = pg.sprite.spritecollideany(self, level.enemy_group)
        if sprite:
            if self.rect.top > sprite.rect.top:
                self.change_to_explode()
            else:
                self.rect.bottom = sprite.rect.y
                self.y_vel = -8
                if self.direction == c.RIGHT:
                    self.x_vel = 15
                else:
                    self.x_vel = -15
                self.state = c.BOUNCING
        elif enemy:
            if enemy.name != c.FIRESTICK:
                level.update_score(100, enemy, 0)
                level.move_to_dying_group(level.enemy_group, enemy)
                enemy.start_death_jump(self.direction)
            self.change_to_explode()

    def change_to_explode(self):
        """Change the state to exploding."""
        self.frame_index = 4
        self.state = c.EXPLODING
