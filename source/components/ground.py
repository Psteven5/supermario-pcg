from . import stuff
from .. import setup, constants as c

class Ground(stuff.Stuff):
    def __init__(self,x,  y  , color=c.ORANGE, group=None, name=c.MAP_GROUND):
        orange_rect = [(0, 0, 16, 16)]
        green_rect = [(208, 32, 16, 16)]
        # Set the frame rectangles based on the brick's color

        if color == c.ORANGE:
            frame_rect = orange_rect
        else:
            frame_rect = green_rect
                # Initialize the ground sprite using the parent class Stuff
        stuff.Stuff.__init__(self, x, y, setup.GFX['tile_set'],frame_rect, c.BRICK_SIZE_MULTIPLIER)
        self.name = name

