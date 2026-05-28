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
    def __init__(self, chunk_size, chances=dict(), difficulty=1):
        self.chunk_size = chunk_size
        self.GROUND_Y = 538
        self.map_data = None
        self.difficulty = int(difficulty)

        # Chances for different level components (between 0.0 and 1.0)
        # given an array chances:
        # 0 - gaps, 1 - pipe/stairs, 2 - bricks, 3 - boxes, 4 - enemies, 5 - chunk is only bricks, 6 - chunk is split in two
        if len(chances) >= 7:
            # Filtering in case a value is not inbetween 0.0 and 1.0
            for chance in chances:
                chances[chance] = chances[chance] if 0.0 <= chances[chance] <= 1.0 else 0.0

            self.gaps_chance = chances['gaps']
            self.pipestairs_chance = chances['pipestairs']
            self.bricks_chance = chances['bricks']
            self.box_chance = chances['boxes']
            self.enemies_chance = chances['enemies']
            self.chunk_bricks_chance = chances['chunk_bricks']
            self.chunk_split_chance = chances['chunk_split']
        else:
            # Default values
            self.gaps_chance = 0.3
            self.pipestairs_chance = 0.5
            self.bricks_chance = 0.5
            self.box_chance = 0.1
            self.enemies_chance = 0.3
            self.chunk_bricks_chance = 0.0
            self.chunk_split_chance = 0.0

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
        """Choose to either generate a normal level or a brick chunk level"""
        if random.random() < self.chunk_bricks_chance:
            self.generate_chunk_bricks(first)
        elif random.random() < self.chunk_split_chance:
            self.generate_chunk_split(first)
        else:
            self.generate_chunk_normal(first)

    def generate_chunk_normal(self, first=False):
        """Generate a normal chunk."""
        self.current_x = 0
        target_width = self.chunk_size
        segment_length_choices = [s*c.FLOOR_BRICK_SIZE for s in range(c.MIN_FLOOR_DISTANCE, c.MAX_FLOOR_DISTANCE+1)]
        ground_segments = [[0,0]]

        # If first chunk (starting position), generate only ground only first
        if first:
            self.generate_ground(c.START_GEN_OFFSET)
            ground_segments = [[c.START_GEN_OFFSET, c.START_GEN_OFFSET]]

        # First generate the ground
        while self.current_x < target_width:
            segment_length = random.choice(segment_length_choices)
            if segment_length > target_width - self.current_x:
                segment_length = target_width - self.current_x
                ground_segments[-1][1] += segment_length
                self.generate_ground(segment_length)
                continue
            
            # Add the solid ground
            self.generate_ground(segment_length)
            ground_segments[-1][1] += segment_length

            # Random chance to place a gap
            if self.current_x < target_width - c.MAX_GAP_DISTANCE:
                if random.random() < self.gaps_chance:                    
                    gap_distance_choice = random.randint(c.MIN_GAP_BRICKS, c.MAX_GAP_BRICKS)
                    self.current_x += gap_distance_choice * c.BRICK_SIZE
                    new_start_x = ground_segments[-1][1] + gap_distance_choice*c.BRICK_SIZE
                    ground_segments.append([new_start_x, new_start_x])
        
        # Then generate other objects, such as pipes, staircases, bricks
        for seg in ground_segments:
            self.current_x = seg[0] + 100   # +100 to prevent overlap 

            while self.current_x < seg[1]:
                
                # Whether to generate bricks and the y position if done so
                gen_bricks = True
                brick_height = random.randint(c.MIN_GEN_HEIGHT, c.MAX_GEN_HEIGHT)

                # Whether to generate box with power-ups or coins
                gen_box = True

                # Random chance to place a pipe or stairs
                if random.random() < self.pipestairs_chance:
                    # 50/50 chance for either pipe or stairs
                    if random.random() < 0.5 and self.current_x + c.PIPE_WIDTH < seg[1]: # Pipe
                        height_type_choice = random.randint(0,2)
                        brick_height += self.generate_pipe(height_type_choice)

                    elif self.current_x + c.STAIR_SIZE * c.STAIR_STEPS_MAX < seg[1]: # Stairs
                        direction_choice = random.randint(0,1)
                        steps_choice = random.randint(c.STAIR_STEPS_MIN, c.STAIR_STEPS_MAX)
                        self.generate_step(steps_choice, direction_choice)
                        self.current_x += steps_choice * c.STAIR_SIZE
                        gen_bricks = False # no bricks above stairs
                
                # Random chance to place bricks
                if gen_bricks and random.random() < self.bricks_chance and self.current_x + c.BRICKS_WIDTH_MAX * c.BRICK_SIZE < seg[1]:
                    bricks_width_choice = random.randint(c.BRICKS_WIDTH_MIN, c.BRICKS_WIDTH_MAX)
                    self.generate_brick(brick_height, bricks_width_choice)
                    self.current_x += bricks_width_choice * c.BRICK_SIZE
                    gen_box = False
                
                # Random chance to place boxes with powerups
                if gen_box and random.random() < self.box_chance and self.current_x + c.BRICK_SIZE < seg[1]:
                    self.generate_box(brick_height) #Misschien ook width toevoegen zodat het een rijtje is
                    self.current_x += c.BRICK_SIZE

                self.current_x += random.choice(segment_length_choices)

        self.generate_enemy()
        self.generate_slider()
        self.generate_checkpoint()
        self.save_chunk()

    def generate_chunk_bricks(self, first=False):
        """Generate a brick chunk, without ground (depending on start chunk)."""
        self.current_x = 0
        target_width = self.chunk_size
        current_height = 450  # about the height of the ground
        bricks_segments = []
        first_brick = True
        
        # If first chunk (starting position), generate only ground only first
        if first:
            self.generate_ground(c.START_GEN_OFFSET)

        self.current_x += random.randint(c.BRICK_CHUNK_MIN_GAP, c.BRICK_CHUNK_MAX_GAP)

        # Generate rows of bricks
        while self.current_x < target_width:
            bricks_width_choice = random.randint(c.BRICK_CHUNK_WIDTH_MIN, c.BRICK_CHUNK_WIDTH_MAX)
            while self.current_x + bricks_width_choice * c.BRICK_SIZE > target_width:
                bricks_width_choice -= 1

            # Check whether bricks can still be placed at the end
            if bricks_width_choice <= 0:
                break

            # Determine the difference wrt height to the last brick row
            if first_brick:
                first_brick = False
            else:
                height_diff_choice = random.randint(c.BRICK_CHUNK_MIN_HEIGHT_DIFF, c.BRICK_CHUNK_MAX_HEIGHT_DIFF)
                # 50/50 chance to add or subtract height
                if random.random() < 0.5:
                    height_diff_choice = -height_diff_choice

                height_range = c.BRICK_CHUNK_MAX_HEIGHT - c.BRICK_CHUNK_MIN_HEIGHT
                shifted_height = current_height + height_diff_choice - c.BRICK_CHUNK_MIN_HEIGHT
                current_height = c.BRICK_CHUNK_MIN_HEIGHT + height_range - abs(height_range - shifted_height%(2*height_range))

            # Generate brick series, and keep a log of brick segments (start x, end x, height y)
            bricks_segments.append([self.current_x, self.current_x, current_height])
            self.generate_chunk_brick_series(current_height, bricks_width_choice)
            self.current_x += bricks_width_choice * c.BRICK_SIZE
            bricks_segments[-1][1] = self.current_x
            
            # Gap between bricks
            gap_width_choice = random.randint(c.BRICK_CHUNK_MIN_GAP, c.BRICK_CHUNK_MAX_GAP)
            self.current_x += gap_width_choice * c.BRICK_SIZE

        self.generate_chunk_brick_enemies(bricks_segments)
        self.generate_checkpoint()
        self.save_chunk()

    def generate_chunk_split(self, first=False):
        """Generate a two-lane chunk with one easy lane and one hard lane."""
        self.current_x = 0
        target_width = self.chunk_size
        easy_lane = random.choice(["upper", "lower"])
        hard_lane = "lower" if easy_lane == "upper" else "upper"

        upper_steps = c.STAIR_STEPS_MAX + 2.5
        upper_y = self.GROUND_Y - upper_steps * c.STAIR_SIZE
        entry_x = c.START_GEN_OFFSET if first else c.STAIR_SIZE * 2
        entry_x = min(entry_x, target_width // 4)
        upper_start = entry_x + 2 * c.BRICK_SIZE
        exit_x = target_width - 3 * c.STAIR_SIZE
        upper_end = exit_x

        def add_ground_segment(start_x, end_x):
            if end_x <= start_x:
                return
            self.current_x = start_x
            self.generate_ground(end_x - start_x)

        def add_upper_segment(start_x, end_x):
            if end_x <= start_x:
                return
            self.current_x = start_x
            self.generate_chunk_brick_series(upper_y, (end_x - start_x) // c.BRICK_SIZE)

        def make_segments(start_x, end_x, hard=False):
            if not hard:
                return [[start_x, end_x]]

            segments = []
            current_x = start_x
            while current_x < end_x:
                segment_length = random.randint(4, 9) * c.BRICK_SIZE
                segment_end = min(current_x + segment_length, end_x)
                segments.append([current_x, segment_end])
                current_x = segment_end

                if current_x < end_x:
                    gap_width = random.randint(c.MIN_GAP_BRICKS, c.MAX_GAP_BRICKS - 1) * c.BRICK_SIZE
                    current_x = min(current_x + gap_width, end_x)

            return segments

        def add_enemy(x_pos, y_pos, enemy_type, range_start=None, range_end=None):
            enemy = {
                "x": int(x_pos),
                "y": int(y_pos),
                "direction": 0,
                "type": enemy_type,
                "color": 0,
                "num": 1
            }

            if range_start is not None and range_end is not None:
                enemy["range"] = 1
                enemy["range_start"] = int(range_start)
                enemy["range_end"] = int(range_end)

            group_index = len(self.chunk[c.MAP_ENEMY])
            self.chunk[c.MAP_ENEMY].append({str(group_index): [enemy]})

        def add_easy_bonus(lane):
            if random.random() > 0.35:
                return

            self.current_x = random.randint(upper_start, max(upper_start, upper_end - c.BRICK_SIZE))
            height = self.GROUND_Y - (upper_y - 90) if lane == "upper" else random.randint(c.MIN_GEN_HEIGHT, c.MAX_GEN_HEIGHT)
            self.generate_box(height)

        def add_lower_obstacles(segments):
            enemy_types = min(self.difficulty, 2)
            for start_x, end_x in segments:
                current_x = max(start_x + 120, c.SCREEN_WIDTH + 100)
                while current_x < end_x - 120:
                    self.current_x = current_x

                    if random.random() < 0.45 and current_x + c.PIPE_WIDTH < end_x:
                        self.generate_pipe(random.randint(0, 2))
                        current_x += c.PIPE_WIDTH + random.randint(80, 140)
                        continue

                    if random.random() < 0.75:
                        enemy_type = random.randint(0, enemy_types)
                        add_enemy(current_x, self.GROUND_Y - 40, enemy_type, current_x - 120, current_x + 160)

                    if random.random() < 0.4 and current_x + c.BRICKS_WIDTH_MAX * c.BRICK_SIZE < end_x:
                        self.generate_brick(random.randint(c.MIN_GEN_HEIGHT, c.MAX_GEN_HEIGHT), random.randint(2, c.BRICKS_WIDTH_MAX))

                    current_x += random.randint(130, 230)

        def add_upper_obstacles(segments):
            for start_x, end_x in segments:
                current_x = start_x + 80
                while current_x < end_x - 100:
                    if random.random() < 0.8:
                        add_enemy(current_x, upper_y - 40, c.ENEMY_TYPE_KOOPA, start_x, end_x)

                    if random.random() < 0.55:
                        self.current_x = current_x + c.BRICK_SIZE
                        obstacle_y = upper_y - 95
                        self.chunk[c.MAP_BRICK].append({
                            "x": self.current_x,
                            "y": obstacle_y,
                            "type": 0
                        })

                    current_x += random.randint(120, 210)

        if hard_lane == "lower":
            lower_segments = [[0, upper_start]]
            lower_segments += make_segments(upper_start, exit_x, True)
            lower_segments.append([exit_x, target_width])
        else:
            lower_segments = make_segments(0, target_width)

        upper_segments = make_segments(upper_start, upper_end)

        # A small block lip and one jump block mark the upper path without making stairs.
        self.chunk[c.MAP_BRICK].append({
            "x": entry_x - c.BRICK_SIZE,
            "y": upper_y + 2 * c.BRICK_SIZE,
            "type": 0
        })
        self.current_x = entry_x
        self.generate_chunk_brick_series(upper_y, 2)

        for start_x, end_x in lower_segments:
            add_ground_segment(start_x, end_x)

        for start_x, end_x in upper_segments:
            add_upper_segment(start_x, end_x)

        if hard_lane == "lower":
            add_lower_obstacles(lower_segments[1:-1])
            add_easy_bonus("upper")
        else:
            add_upper_obstacles(upper_segments)
            add_easy_bonus("lower")

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
        pipe_top = self.GROUND_Y - h
        
        self.chunk[c.MAP_PIPE].append({
            "x": self.current_x,
            "y": pipe_top,
            "width": 82,
            "height": h,
            "type": 0
        })
        return h

    def generate_step(self, steps, direction=0):
        """Generates a staircase of blocks. 0 is up, 1 is down."""
        base_x = self.current_x
        for i in range(steps):
            step_h = (i + 1) * c.STAIR_SIZE
            curr_x = base_x + (i * 43) if direction == 0 else base_x + ((steps - i) * 43)
            self.chunk[c.MAP_STEP].append({
                "x": curr_x,
                "y": self.GROUND_Y - step_h,
                "width": 43,
                "height": step_h
            })

    def generate_brick(self, height, num_bricks):
        """Generates a series of bricks."""
        base_x = self.current_x
        for i in range(num_bricks):
            curr_x = base_x + i * c.BRICK_SIZE
            # Make a random block in the bricks a box
            if random.random() < 0.05:
                block_type = [1,3,6]
                if self.difficulty > 2:
                    block_type = [1,3,4,6]
                if self.difficulty > 3:
                    block_type = [1,2,3,4,6] # TODO STAR WERKT NOG NIET
                self.chunk[c.MAP_BOX].append({
                    "x": curr_x,
                    "y": self.GROUND_Y - height,
                    "type": random.choice(block_type)
                })
            else:
                self.chunk[c.MAP_BRICK].append({
                "x": curr_x,
                "y": self.GROUND_Y - height,
                "type": 0
            })
                
    def generate_chunk_brick_series(self, height, num_bricks):
        """Generates a series of bricks."""
        base_x = self.current_x
        for i in range(num_bricks):
            curr_x = base_x + i * c.BRICK_SIZE
            self.chunk[c.MAP_BRICK].append({
                "x": curr_x,
                "y": height,
                "type": 0
            })


    def generate_box(self, height):
        base_x = self.current_x
        curr_x = base_x + c.BRICK_SIZE
        block_type = [1,3,6]
        if self.difficulty > 2:
            block_type = [1,3,4,6]
        if self.difficulty > 3:
            block_type = [1,2,3,4,6] # TODO STAR WERKT NOG NIET
        self.chunk[c.MAP_BOX].append({
            "x": curr_x,
            "y": self.GROUND_Y - height,
            "type": random.choice(block_type)
        })

    def generate_enemy(self):
        enemy_list = self.chunk[c.MAP_ENEMY]        
        safe_start_x = c.SCREEN_WIDTH + 100
        enemy_types = min(self.difficulty, c.ENEMY_TYPE_FLY_KOOPA)
        # 0 Goomba, 1 Koopa, 2 Koopa flying, 3 piranha plant, 4 firestick, 5 bowser
        # Generate enemies across all ground segments.
        for seg in self.chunk[c.MAP_GROUND]:
            start_x = seg["x"]
            end_x = seg["x"] + seg["width"]

            current_x = max(start_x + 150, safe_start_x)  # avoid edges and the first visible area of each chunk

            while current_x < end_x - 150:
                
                # To check whether we are close to stairs or pipes (we do not spawn enemies here)
                close_to_pipestairs = False

                for step in self.chunk[c.MAP_STEP]:
                    if abs(current_x - step['x']) < 200:
                        close_to_pipestairs = True
                        break
                for pipe in self.chunk[c.MAP_PIPE]:
                    if abs(current_x - pipe['x']) < 100:
                        close_to_pipestairs = True
                        break

                # Randomly decide to place a random type of enemy
                if random.random() < self.enemies_chance and not close_to_pipestairs:
                    enemy_type = random.randint(0, enemy_types)
                    enemy = {
                        "x": int(current_x),
                        "y": int(self.GROUND_Y - 40),
                        "direction": 0,
                        "type": enemy_type,
                        "color": 0,
                        "num": 1
                    }

                    # Optional movement behavior
                    if enemy_type == c.ENEMY_TYPE_KOOPA:
                        # Also determine the distance to a pipe
                        min_range_start = 250  # equals the max values of range_start and range_end
                        min_range_end = 250    # TODO: declare constants for enemy range?

                        for pipe in self.chunk[c.MAP_PIPE]: 
                            distance_to_pipe = pipe['x'] - current_x
                            if abs(distance_to_pipe) < 250:
                                if distance_to_pipe < 0 and -distance_to_pipe < min_range_start:
                                    min_range_start = -distance_to_pipe
                                elif distance_to_pipe < min_range_end:
                                    min_range_end = distance_to_pipe

                        enemy["range"] = 1
                        enemy["range_start"] = int(min(current_x - min_range_start, current_x - random.randint(100, 250)))
                        enemy["range_end"] = int(min(current_x + min_range_end, current_x + random.randint(100, 250)))

                    elif enemy_type == c.ENEMY_TYPE_FLY_KOOPA:
                        enemy["range"] = 1
                        enemy["range_start"] = int(self.GROUND_Y - random.randint(200, 400))
                        enemy["range_end"] = int(self.GROUND_Y - random.randint(50, 150))
                        enemy["is_vertical"] = 1

                    group_index = len(enemy_list)
                    enemy_list.append({str(group_index): [enemy]})

                    # spacing between enemies
                    current_x += random.randint(150, 250)

                current_x += random.randint(80, 150)
    
    def generate_chunk_brick_enemies(self, bricks_segments):
        enemy_list = self.chunk[c.MAP_ENEMY]
        safe_start_x = c.SCREEN_WIDTH + 100
        
        # Ignore the first few bricks
        if len(bricks_segments) > 2:
            bricks_segments = bricks_segments[2:]
        
        for seg in bricks_segments:
            start_x = seg[0]
            end_x = seg[1]
            height = seg[2]
            
            # If bricks series too small, skip
            if start_x >= end_x:
                continue

            x_pos = random.randint(start_x, end_x)
            if random.random() < self.enemies_chance:
                enemy_type = c.ENEMY_TYPE_KOOPA  # Koopa
                enemy = {
                    "x": int(x_pos),
                    "y": int(height - 40),
                    "direction": 0,
                    "type": enemy_type,
                    "color": 1,
                    "num": 1,
                    "range": 1,
                    "range_start": start_x,
                    "range_end": end_x,
                }
                
                group_index = len(enemy_list)
                enemy_list.append({str(group_index): [enemy]})
        
        print(enemy_list)



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

            # Spawn before the enemy enters the visible screen.
            checkpoint_x = max(0, first_enemy_x - c.SCREEN_WIDTH + 100)
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
