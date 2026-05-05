import json
import random
import os
#from .. import setup, tools
#from .. import constants as c
#from ..components import info, stuff, player, brick, box, enemy, powerup, coin

# TODO: add constants to constants.py
MIN_FLOOR_DISTANCE = 200
MAX_FLOOR_DISTANCE = 1000
MIN_GEN_DISTANCE = 100
MAX_GEN_DISTANCE = 200
MIN_GEN_HEIGHT = 20
MAX_GEN_HEIGHT = 100
GAP_DISTANCE = 200
PIPE_WIDTH = 83
STAIR_WIDTH = 43
STAIR_STEPS = 4

# TODO: add bricks, enemies, etc.

class LevelGenerator:
    def __init__(self):
        # Constants
        self.CHUNK_WIDTH = 5000 
        self.GROUND_Y = 538
        self.level_data = {
            "image_name": "level_1",
            "maps": [{"start_x": 0, "end_x": 0, "player_x": 110, "player_y": 538}],
            "ground": [],
            "pipe": [],
            "step": [],
            "coin": [],
            "brick": [],
            "box": [],
            "enemy": [],
            "checkpoint": [],
            "flagpole": []
        }
        self.current_x = 0

    def add_flat_ground(self, width):
        """Adds basic floor."""
        self.level_data["ground"].append({
            "x": self.current_x, 
            "y": self.GROUND_Y, 
            "width": width, 
            "height": 60
        })
        self.current_x += width

    def add_pipe_section(self, height_type):
        """Adds a pipe at a relative offset."""
        # height_type 0: small, 1: medium, 2: large
        heights = [84, 126, 170]
        h = heights[height_type]
        self.level_data["pipe"].append({
            "x": self.current_x,
            "y": self.GROUND_Y - h,
            "width": 83,
            "height": h,
            "type": 0
        })

    def add_staircase(self, steps, direction=0):
        """Generates a staircase of blocks. 0 is up, 1 is down"""
        base_x = self.current_x
        for i in range(steps):
            step_h = (i + 1) * 43
            curr_x = base_x + (i * 40) if direction == 0 else base_x + ((steps - i) * 40)
            self.level_data["step"].append({
                "x": curr_x,
                "y": self.GROUND_Y - step_h,
                "width": 40,
                "height": step_h
            })

    def generate(self):
        """Generate the level."""
        self.current_x = 0
        target_width = self.CHUNK_WIDTH
        ground_segments = [[0,0]]

        # First generate the ground
        while self.current_x < target_width:
            segment_length = random.randint(MIN_FLOOR_DISTANCE, MAX_FLOOR_DISTANCE)
            if segment_length > target_width - self.current_x:
                segment_length = target_width - self.current_x
                self.add_flat_ground(segment_length)
                continue

            # Add the solid ground
            self.add_flat_ground(segment_length)
            ground_segments[-1][1] += segment_length
            
            # Random chance to place a gap
            if self.current_x < target_width - GAP_DISTANCE:
                if random.random() < 0.3:                    
                    self.current_x += GAP_DISTANCE
                    new_start_x = ground_segments[-1][1] + GAP_DISTANCE
                    ground_segments.append([new_start_x, new_start_x])
        
        print(ground_segments)
        
        # Then generate other objects, such as pipes and staircases
        for seg in ground_segments:
            self.current_x = seg[0] + 100   
            #seg_current_x += random.randint(MIN_GEN_DISTANCE, MAX_GEN_DISTANCE)

            while self.current_x < seg[1]:
                gen_distance = random.randint(MIN_GEN_DISTANCE, MAX_GEN_DISTANCE)

                # Random chance to place a pipe or stairs
                if random.random() < 0.2 and self.current_x + PIPE_WIDTH < seg[1]: # Pipe
                    height_type_choice = random.randint(0,2)
                    self.add_pipe_section(height_type_choice)
                elif random.random() < 0.3 and self.current_x + STAIR_WIDTH*STAIR_STEPS < seg[1]: # Stairs
                    direction_choice = random.randint(0,1)
                    self.add_staircase(5, direction_choice)
                    self.current_x += STAIR_STEPS * STAIR_WIDTH

                self.current_x += random.randint(MIN_GEN_DISTANCE, MAX_GEN_DISTANCE)


    def save(self, filename="level_generated.json"):
        # Update map end_x based on final current_x
        self.level_data["maps"][0]["end_x"] = self.current_x
        
        with open(filename, 'w') as f:
            json.dump(self.level_data, f, indent=4)
        print(f"Level saved to {filename}")

# TODO: use LevelGenerator in level.py
gen = LevelGenerator()
gen.generate()
gen.save("level_1.json")