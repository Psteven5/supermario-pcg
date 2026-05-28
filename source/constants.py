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
# Our constants

CHUNK_SIZE = 4988
SHIFT_THRESHOLD = CHUNK_SIZE

__author__ = 'm0rniac'

DEBUG = False
DEBUG_START_X = 110
DEBUG_START_y = 538

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
SCREEN_SIZE = (SCREEN_WIDTH,SCREEN_HEIGHT)

ORIGINAL_CAPTION = "Super Mario Bros (Python Clone) by m0rniac"

## COLORS ##
#                R    G    B
GRAY         = (100, 100, 100)
NAVYBLUE     = ( 60,  60, 100)
WHITE        = (255, 255, 255)
RED          = (255,   0,   0)
GREEN        = (  0, 255,   0)
FOREST_GREEN = ( 31, 162,  35)
BLUE         = (  0,   0, 255)
SKY_BLUE     = ( 39, 145, 251)
YELLOW       = (255, 255,   0)
ORANGE       = (255, 128,   0)
PURPLE       = (255,   0, 255)
CYAN         = (  0, 255, 255)
BLACK        = (  0,   0,   0)
NEAR_BLACK   = ( 19,  15,  48)
COMBLUE      = (233, 232, 255)
GOLD         = (255, 215,   0)

BGCOLOR = WHITE


SIZE_MULTIPLIER = 2.5
BRICK_SIZE_MULTIPLIER = 2.69
BACKGROUND_MULTIPLER = 2.679
GROUND_HEIGHT = SCREEN_HEIGHT - 62

GAME_TIME_OUT = 301

#STATES FOR ENTIRE GAME
MAIN_MENU = 'main menu'
LOAD_SCREEN = 'load screen'
TIME_OUT = 'time out'
GAME_OVER = 'you are loser aymen uss'
LEVEL = 'level'

#MAIN MENU CURSOR STATES
PLAYER1 = '1 PLAYER GAME'
PLAYER2 = '2 PLAYER GAME'

#GAME INFO DICTIONARY KEYS
COIN_TOTAL = 'coin total'
SCORE = 'score'
TOP_SCORE = 'top score'
LIVES = 'lives'
CURRENT_TIME = 'current time'
LEVEL_NUM = 'level num'
PLAYER_NAME = 'player name'
PLAYER_MARIO = 'mario'
PLAYER_LUIGI = 'luigi'

#MAP COMPONENTS
MAP_IMAGE = 'image_name'
MAP_MAPS = 'maps'
SUB_MAP = 'sub_map'
MAP_GROUND = 'ground'
MAP_PIPE = 'pipe'
PIPE_TYPE_NONE = 0
PIPE_TYPE_IN = 1                # can go down in the pipe
PIPE_TYPE_HORIZONTAL = 2        # can go right in the pipe
MAP_STEP = 'step'
MAP_BRICK = 'brick'
BRICK_NUM = 'brick_num'
TYPE_NONE = 0
TYPE_COIN = 1
TYPE_STAR = 2
MAP_BOX = 'box'
TYPE_MUSHROOM = 3
TYPE_FIREFLOWER = 4
TYPE_FIREBALL = 5
TYPE_LIFEMUSHROOM = 6
MAP_ENEMY = 'enemy'
ENEMY_TYPE_GOOMBA = 0
ENEMY_TYPE_KOOPA = 1
ENEMY_TYPE_FLY_KOOPA = 2
ENEMY_TYPE_PIRANHA = 3
ENEMY_TYPE_FIRESTICK = 4
ENEMY_TYPE_FIRE_KOOPA = 5
ENEMY_RANGE = 'range'
MAP_CHECKPOINT = 'checkpoint'
ENEMY_GROUPID = 'enemy_groupid'
MAP_INDEX = 'map_index'
CHECKPOINT_TYPE_ENEMY = 0
CHECKPOINT_TYPE_FLAG = 1
CHECKPOINT_TYPE_CASTLE = 2
CHECKPOINT_TYPE_MUSHROOM = 3
CHECKPOINT_TYPE_PIPE = 4        # trigger player to go right in a pipe
CHECKPOINT_TYPE_PIPE_UP = 5     # trigger player to another map and go up out of a pipe
CHECKPOINT_TYPE_MAP = 6         # trigger player to go to another map
CHECKPOINT_TYPE_BOSS = 7        # defeat the boss
MAP_FLAGPOLE = 'flagpole'
FLAGPOLE_TYPE_FLAG = 0
FLAGPOLE_TYPE_POLE = 1
FLAGPOLE_TYPE_TOP = 2
MAP_SLIDER = 'slider'
HORIZONTAL = 0
VERTICAL = 1
VELOCITY = 'velocity'
MAP_COIN = 'coin'

#COMPONENT COLOR
COLOR = 'color'
COLOR_TYPE_ORANGE = 0
COLOR_TYPE_GREEN = 1
COLOR_TYPE_RED = 2

#BRICK STATES
RESTING = 'resting'
BUMPED = 'bumped'
OPENED = 'opened'

#MUSHROOM STATES
REVEAL = 'reveal'
SLIDE = 'slide'

#Player FRAMES
PLAYER_FRAMES = 'image_frames'
RIGHT_SMALL_NORMAL = 'right_small_normal'
RIGHT_BIG_NORMAL = 'right_big_normal'
RIGHT_BIG_FIRE = 'right_big_fire'

#PLAYER States
STAND = 'standing'
WALK = 'walk'
JUMP = 'jump'
FALL = 'fall'
FLY = 'fly'
SMALL_TO_BIG = 'small to big'
BIG_TO_FIRE = 'big to fire'
BIG_TO_SMALL = 'big to small'
FLAGPOLE = 'flag pole'
WALK_AUTO = 'walk auto'     # not handle key input in this state
END_OF_LEVEL_FALL = 'end of level fall'
IN_CASTLE = 'in castle'
DOWN_TO_PIPE = 'down to pipe'
UP_OUT_PIPE = 'up out of pipe'

#PLAYER FORCES
PLAYER_SPEED = 'speed'
WALK_ACCEL = 'walk_accel'
RUN_ACCEL = 'run_accel'
JUMP_VEL = 'jump_velocity'
MAX_Y_VEL = 'max_y_velocity'
MAX_RUN_SPEED = 'max_run_speed'
MAX_WALK_SPEED = 'max_walk_speed'
SMALL_TURNAROUND = .35
JUMP_GRAVITY = .31
GRAVITY = 1.01

#LIST of ENEMIES
GOOMBA = 'goomba'
KOOPA = 'koopa'
FLY_KOOPA = 'fly koopa'
FIRE_KOOPA = 'fire koopa'
FIRE = 'fire'
PIRANHA = 'piranha'
FIRESTICK = 'firestick'

#GOOMBA Stuff
LEFT = 'left'
RIGHT = 'right'
JUMPED_ON = 'jumped on'
DEATH_JUMP = 'death jump'

#KOOPA STUFF
SHELL_SLIDE = 'shell slide'

#FLAG STATE
TOP_OF_POLE = 'top of pole'
SLIDE_DOWN = 'slide down'
BOTTOM_OF_POLE = 'bottom of pole'

#FIREBALL STATE
FLYING = 'flying'
BOUNCING = 'bouncing'
EXPLODING = 'exploding'

#IMAGE SHEET
ENEMY_SHEET = 'smb_enemies_sheet'
ITEM_SHEET = 'item_objects'

# Constants for generate_chunk.py
FLOOR_BRICK_SIZE = 43
MIN_FLOOR_DISTANCE = 5  # Minimum number of bricks for floor
MAX_FLOOR_DISTANCE = 20 # Maximum number of bricks for floor

MIN_GEN_DISTANCE = 100
MAX_GEN_DISTANCE = 200
MIN_GEN_HEIGHT = 150  # for bricks
MAX_GEN_HEIGHT = 200
START_GEN_OFFSET = 9*FLOOR_BRICK_SIZE # offset of generation wrt the player starting position

MIN_GAP_BRICKS = 4  # how many bricks there would fit in a gap
MAX_GAP_BRICKS = 7
MIN_GAP_DISTANCE = MIN_GAP_BRICKS*FLOOR_BRICK_SIZE
MAX_GAP_DISTANCE = MAX_GAP_BRICKS*FLOOR_BRICK_SIZE
PIPE_WIDTH = 83
STAIR_SIZE = 43
STAIR_STEPS_MIN = 3
STAIR_STEPS_MAX = 4
BRICKS_WIDTH_MIN = 3
BRICKS_WIDTH_MAX = 6
BRICK_SIZE = 43

# Constants for the brick chunk in generate_chunk.py
BRICK_CHUNK_MIN_HEIGHT_DIFF = 30
BRICK_CHUNK_MAX_HEIGHT_DIFF = 100
BRICK_CHUNK_MIN_HEIGHT = 50
BRICK_CHUNK_MAX_HEIGHT = 450
BRICK_CHUNK_WIDTH_MIN = 3
BRICK_CHUNK_WIDTH_MAX = 8
BRICK_CHUNK_MIN_GAP = 2
BRICK_CHUNK_MAX_GAP = 5
BRICK_CHUNK_MIN_GAP_DIST = BRICK_CHUNK_MIN_GAP*FLOOR_BRICK_SIZE
BRICK_CHUNK_MAX_GAP_DIST = BRICK_CHUNK_MAX_GAP*FLOOR_BRICK_SIZE
BRICK_CHUNK_ENEMY_MARGIN = 40

# Split chunk
SPLIT_CHUNK_MIN_GAP_BRICKS = 3
SPLIT_CHUNK_MAX_GAP_BRICKS = 4

# Constants for starting chances per chunk
CHANCE_GAP = 0.05
CHANCE_PIPESTAIRS = 0.4
CHANCE_BRICKS = 0.5
CHANCE_BOXES = 0.5
CHANCE_ENEMIES = 0.1
CHANCE_BRICKS_CHUNK = 0.0
CHANCE_SPLIT_CHUNK = 0.0

# Chances per chunk that we want to approach as difficulty increases
END_CHANCE_GAP = 0.6
END_CHANCE_PIPESTAIRS = 0.6
END_CHANCE_BRICKS = 0.7
END_CHANCE_BOXES = 0.2
END_CHANCE_ENEMIES = 0.8
END_CHANCE_BRICKS_CHUNK = 0.3
END_CHANCE_SPLIT_CHUNK = 0.3

# Weights for difficulty increase per item
WEIGHT_GAP = 2
WEIGHT_PIPESTAIRS = 1.2
WEIGHT_BRICKS = 1
WEIGHT_BOXES = 2
WEIGHT_ENEMIES = 1.8
WEIGHT_BRICKS_CHUNK = 3
WEIGHT_SPLIT_CHUNK = 4


EULER_NUM = 2.71828
MAX_DIFFICULTY = 5