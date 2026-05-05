# maps
# ground
# pipe 
# step 
# coin 
# brick 
# box 
# enemy
import json
import random
import os

from .. import constants as c


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

class GenerateChunk():
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        self.GROUND_Y = 538
        self.map_data = None

        self.chunk = {
            c.MAP_IMAGE: "level_1",
            c.MAP_MAPS: [{"start_x": 0, "end_x": self.chunk_size, "player_x": 110, "player_y": 538}],
            c.MAP_GROUND: [],
            c.MAP_PIPE: [],
            c.MAP_STEP: [],
            c.MAP_BRICK: [],
            c.MAP_BOX: [],
            c.MAP_ENEMY: [],
            c.MAP_SLIDER: [],
            c.MAP_CHECKPOINT: []
        }
        self.current_x = 0

    def generate_chunk(self):
        """Generate the level."""
        self.current_x = 0
        target_width = self.chunk_size
        ground_segments = [[0,0]]

        # First generate the ground
        while self.current_x < target_width:
            segment_length = random.randint(MIN_FLOOR_DISTANCE, MAX_FLOOR_DISTANCE)
            if segment_length > target_width - self.current_x:
                segment_length = target_width - self.current_x
                ground_segments[-1][1] += segment_length
                self.generate_ground(segment_length)
                continue
            
            # Add the solid ground
            self.generate_ground(segment_length)
            ground_segments[-1][1] += segment_length

            # Random chance to place a gap
            if self.current_x < target_width - GAP_DISTANCE:
                if random.random() < 0.3:                    
                    self.current_x += GAP_DISTANCE
                    new_start_x = ground_segments[-1][1] + GAP_DISTANCE
                    ground_segments.append([new_start_x, new_start_x])
        
        # Then generate other objects, such as pipes and staircases
        for seg in ground_segments:
            self.current_x = seg[0] + 100   
            #seg_current_x += random.randint(MIN_GEN_DISTANCE, MAX_GEN_DISTANCE)

            while self.current_x < seg[1]:
                # Random chance to place a pipe or stairs
                if random.random() < 0.2 and self.current_x + PIPE_WIDTH < seg[1]: # Pipe
                    height_type_choice = random.randint(0,2)
                    self.generate_pipe(height_type_choice)
                elif random.random() < 0.3 and self.current_x + STAIR_WIDTH*STAIR_STEPS < seg[1]: # Stairs
                    direction_choice = random.randint(0,1)
                    self.generate_step(STAIR_STEPS, direction_choice)
                    self.current_x += STAIR_STEPS * STAIR_WIDTH

                self.current_x += random.randint(MIN_GEN_DISTANCE, MAX_GEN_DISTANCE)

        self.generate_brick()
        self.generate_box()
        self.generate_enemy()
        self.generate_slider()
        self.generate_checkpoint()
        self.save_chunk()

    def generate_ground(self, width):
        """Adds basic floor."""
        self.chunk[c.MAP_GROUND].append({
            "x": self.current_x, 
            "y": self.GROUND_Y, 
            "width": width, 
            "height": 60
        })
        self.current_x += width

    def generate_pipe(self, height_type):
        """Adds a pipe at a relative offset."""
        # height_type 0: small, 1: medium, 2: large
        heights = [84, 126, 170]
        h = heights[height_type]
        self.chunk[c.MAP_PIPE].append({
            "x": self.current_x,
            "y": self.GROUND_Y - h,
            "width": 83,
            "height": h,
            "type": 0
        })

    def generate_step(self, steps, direction=0):
        """Generates a staircase of blocks. 0 is up, 1 is down"""
        base_x = self.current_x
        for i in range(steps):
            step_h = (i + 1) * 43
            curr_x = base_x + (i * 40) if direction == 0 else base_x + ((steps - i) * 40)
            self.chunk[c.MAP_STEP].append({
                "x": curr_x,
                "y": self.GROUND_Y - step_h,
                "width": 40,
                "height": step_h
            })

    def generate_brick(self):
        pass

    def generate_box(self):
        pass

    def generate_enemy(self):
        pass

    def generate_slider(self):
        pass

    def generate_checkpoint(self):
        pass
        
    def save_chunk(self):
        map_file = 'chunk.json'
        file_path = os.path.join('source', 'data', 'maps', map_file)
        f = open(file_path, 'w')
        json.dump(self.chunk, f, indent=4)
        print(f"Chunk saved to {file_path}")

