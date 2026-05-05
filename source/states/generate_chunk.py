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
        self.map_data = None

        self.chunk = {
            c.MAP_MAPS: {},
            c.MAP_GROUND: [],
            c.MAP_PIPE: [],
            c.MAP_STEP: [],
            c.MAP_BRICK: [],
            c.MAP_BOX: [],
            c.MAP_ENEMY: [],
            c.MAP_SLIDER: []
        }

    def generate_chunk(self):
        self.generate_map()
        self.generate_ground()
        self.generate_pipe()
        self.generate_step()
        self.generate_brick()
        self.generate_box()
        self.generate_enemy()
        self.generate_slider()
        self.save_chunk()

    def generate_map(self):
        pass

    def generate_ground(self):
        pass

    def generate_pipe(self):
        pass

    def generate_step(self):
        pass

    def generate_brick(self):
        pass

    def generate_box(self):
        pass

    def generate_enemy(self):
        pass

    def generate_slider(self):
        pass
        
    def save_chunk(self):
        map_file = 'chunk.json'
        file_path = os.path.join('source', 'data', 'maps', map_file)
        f = open(file_path, 'w')
        json.dump(self.chunk, f, indent=4)
        print(f"Chunk saved to {file_path}")

