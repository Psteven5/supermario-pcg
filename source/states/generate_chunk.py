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

    def generate_chunk(self, first=False):
        """Generate the level."""
        self.current_x = 0
        target_width = self.chunk_size
        ground_segments = [[0,0]]

        # If first chunk (starting position), generate only ground only first
        if first:
            self.generate_ground(c.START_GEN_OFFSET)
            ground_segments = [[c.START_GEN_OFFSET, c.START_GEN_OFFSET]]

        # First generate the ground
        while self.current_x < target_width:
            segment_length = random.randint(c.MIN_FLOOR_DISTANCE, c.MAX_FLOOR_DISTANCE)
            if segment_length > target_width - self.current_x:
                segment_length = target_width - self.current_x
                ground_segments[-1][1] += segment_length
                self.generate_ground(segment_length)
                continue
            
            # Add the solid ground
            self.generate_ground(segment_length)
            ground_segments[-1][1] += segment_length

            # Random chance to place a gap
            if self.current_x < target_width - c.GAP_DISTANCE:
                if random.random() < 0.3:                    
                    self.current_x += c.GAP_DISTANCE
                    new_start_x = ground_segments[-1][1] + c.GAP_DISTANCE
                    ground_segments.append([new_start_x, new_start_x])
        
        # Then generate other objects, such as pipes, staircases, bricks
        # TODO: add enemies, boxes, sliders etc
        for seg in ground_segments:
            self.current_x = seg[0] + 100   # +100 to prevent overlap 

            while self.current_x < seg[1]:
                
                # Whether to generate bricks and the y position if done so
                gen_bricks = True
                brick_height = random.randint(c.MIN_GEN_HEIGHT, c.MAX_GEN_HEIGHT)

                # Whether to generate box with power-ups or coins
                gen_box = True

                # Random chance to place a pipe, stairs
                if random.random() < 0.2 and self.current_x + c.PIPE_WIDTH < seg[1]: # Pipe
                    height_type_choice = random.randint(0,2)
                    brick_height += self.generate_pipe(height_type_choice)

                elif random.random() < 0.3 and self.current_x + c.STAIR_SIZE * c.STAIR_STEPS < seg[1]: # Stairs
                    direction_choice = random.randint(0,1)
                    self.generate_step(c.STAIR_STEPS, direction_choice)
                    self.current_x += c.STAIR_STEPS * c.STAIR_SIZE
                    gen_bricks = False # no bricks above stairs
                
                # Random chance to place bricks
                if gen_bricks and random.random() < 0.5 and self.current_x + c.BRICKS_WIDTH * c.BRICK_SIZE < seg[1]:
                    self.generate_brick(brick_height, c.BRICKS_WIDTH)
                    self.current_x += c.BRICKS_WIDTH * c.BRICK_SIZE
                    gen_box = False
                
                if gen_box and random.random() < 0.1 and self.current_x + c.BRICKS_WIDTH < seg[1]:
                    self.generate_box(brick_height) #Misschien ook width toevoegen zodat het een rijtje is
                    self.current_x += c.BRICKS_WIDTH #* c.BRICK_SIZE

                self.current_x += random.randint(c.MIN_GEN_DISTANCE, c.MAX_GEN_DISTANCE)

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
        """Adds a pipe at a relative offset. Returns height of the pipe."""
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
        
        return h

    def generate_step(self, steps, direction=0):
        """Generates a staircase of blocks. 0 is up, 1 is down."""
        base_x = self.current_x
        for i in range(steps):
            step_h = (i + 1) * c.STAIR_SIZE
            curr_x = base_x + (i * 40) if direction == 0 else base_x + ((steps - i) * 40)
            self.chunk[c.MAP_STEP].append({
                "x": curr_x,
                "y": self.GROUND_Y - step_h,
                "width": 40,
                "height": step_h
            })

    def generate_brick(self, height, num_bricks):
        """Generates a series of bricks."""
        base_x = self.current_x
        for i in range(num_bricks):
            curr_x = base_x + i * c.BRICK_SIZE
            # Make a random block in the bricks a box
            if random.random() < 0.05:
                self.chunk[c.MAP_BOX].append({
                    "x": curr_x,
                    "y": self.GROUND_Y - height,
                    "type": random.randint(1,6) # Misschien niet alles erin doen
                })
            else:
                self.chunk[c.MAP_BRICK].append({
                "x": curr_x,
                "y": self.GROUND_Y - height,
                "type": 0
            })


    def generate_box(self, height):
        base_x = self.current_x
        curr_x = base_x + c.BRICK_SIZE
        self.chunk[c.MAP_BOX].append({
            "x": curr_x,
            "y": self.GROUND_Y - height,
            "type": random.randint(1,6) # Misschien niet alles erin doen
        })

    def generate_enemy(self):
        enemy_list = self.chunk[c.MAP_ENEMY]

        group = []

        # Generate enemies across all ground segments (one group total)
        for seg in self.chunk[c.MAP_GROUND]:
            start_x = seg["x"]
            end_x = seg["x"] + seg["width"]

            current_x = start_x + 150  # avoid edges

            while current_x < end_x - 150:
                if random.random() < 0.3:
                    enemy_type = random.randint(0, 2)

                    enemy = {
                        "x": int(current_x),
                        "y": int(self.GROUND_Y - 40),
                        "direction": 0,
                        "type": enemy_type,
                        "color": random.randint(0, 2),
                        "num": 1
                    }

                    # Optional movement behavior
                    if enemy_type == 1:
                        enemy["range"] = 1
                        enemy["range_start"] = int(current_x - random.randint(100, 250))
                        enemy["range_end"] = int(current_x + random.randint(100, 250))

                    elif enemy_type == 2:
                        enemy["range"] = 1
                        enemy["range_start"] = int(self.GROUND_Y - random.randint(200, 400))
                        enemy["range_end"] = int(self.GROUND_Y - random.randint(50, 150))
                        enemy["is_vertical"] = 1

                    group.append(enemy)

                    # spacing between enemies
                    current_x += random.randint(150, 250)

                current_x += random.randint(80, 150)

        # Only save group if enemies exist
        if group:
            enemy_list.append({"0": group})

    def generate_slider(self):
        pass

    def generate_checkpoint(self):
        checkpoint_list = self.chunk[c.MAP_CHECKPOINT]
        enemy_list = self.chunk[c.MAP_ENEMY]
        # Add checkpoints for enemies
        for index, group_data in enumerate(enemy_list):

            group_key = str(index)

            # Safety check
            if group_key not in group_data:
                continue

            enemies = group_data[group_key]

            # Skip empty groups
            if not enemies:
                continue

            first_enemy_x = enemies[0]["x"]

            # Spawn before player sees enemies
            checkpoint_x = max(0, first_enemy_x - 600)

            checkpoint_list.append({
                "x": checkpoint_x,
                "y": 0,
                "width": 10,
                "height": 600,
                "type": 0,
                "enemy_groupid": index
            })
        
    def save_chunk(self):
        map_file = 'chunk.json'
        file_path = os.path.join('source', 'data', 'maps', map_file)
        f = open(file_path, 'w')
        json.dump(self.chunk, f, indent=4)
        print(f"Chunk saved to {file_path}")

