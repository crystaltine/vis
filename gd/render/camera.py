import blessed
from typing import TYPE_CHECKING
from render.constants import CameraUtils
from render.utils import fcode
from render.rect import Rect
from math import floor

if TYPE_CHECKING:
    from engine.level import Level

class Camera:

    BG_COLOR = "#0091ff"
    GROUND_COLOR = "#0d7bf1"
    BLOCK_COLOR_1 = "#555"
    BLOCK_COLOR_2 = "#666"

    TEXTURES = {
        "spike": [
            f"{fcode(background=BG_COLOR)} {fcode(foreground='000')}/\\{fcode(background=BG_COLOR)} ",
            f"{fcode(foreground='000')}/__\\"
        ],
        "block": [
            f"{fcode(background=BLOCK_COLOR_1)}    ",
            f"{fcode(background=BLOCK_COLOR_2)}    "
        ]
    }

    def __init__(self, level: "Level"):
        self.term = blessed.Terminal()
        self.left = -CameraUtils.CAMERA_LEFT_OFFSET # since player starts at 0
        self.ground = CameraUtils.DEFAULT_GROUND_LEVEL
        self.level = level

    def draw_obj(self, x: int, y: int, obj_name: str):
        """
        Draws a texture at the specified GRID POSITION on the screen.

        Grid pixel dimensions are defined by `CameraUtils.GRID_PX_X` and `CameraUtils.GRID_PX_Y`.
        (0, 0) is the top left of the CAMERA, for this function.
        (1, 0) would be one block to the right of that (0, 0) 

        Currently supported objects:
        "block"
        "spike"
        """

        # if near edge, dont render
        # TODO - we can add partial rendering later
        if (x < 0 or y < 0 or
            x > CameraUtils.screen_width_blocks(self.term) or
            y > CameraUtils.screen_height_blocks(self.term)):
            return

        obj_texture = Camera.TEXTURES[obj_name]
        refresh_optimization = f"{fcode(background=Camera.BG_COLOR)} "
        # a clever way to not have to rerender the entire bg every time.
        # drawing another bg-colored char makes it "cover up" the old characters
        
        terminal_pos = CameraUtils.grid_to_terminal_pos(x, y)
        
        for i in range(len(obj_texture)):
            print(self.term.move_yx(round(terminal_pos[1]+i), round(terminal_pos[0])) + obj_texture[i] + refresh_optimization)

    def render_init(self):
        """
        Call this once. Draws the background and the floor, 
        which don't need to be updated every frame.
        """
        stuff = [
            Rect(0, 0, 100, 100, self.term, Camera.BG_COLOR), # bg
            Rect(0, 70, 100, 100, self.term, Camera.GROUND_COLOR), # ground
        ]
        [item.render() for item in stuff]
        print("\x1b[0m")

    def render(self):
        """
        Renders a frame onto the screen.
        """
        
        # Only load columns max(0,cam_left) -> cam_left + term_width_lines
        for i in range(
            floor(max(0,self.left)), 
            floor(min(
                len(self.level.leveldata), 
                self.left+CameraUtils.screen_width_blocks(self.term)
            ))
        ):
            level_column = self.level.leveldata[i]

            # these level columns look like this:
            # [OBJECTS.block, OBJECTS.spike, ...],
            # objects are a dict of the format:
            # yellow_grav_portal = {
            #   "hitbox_xrange": [0.1, 0.9],
            #   "hitbox_yrange": [-1.4, 1.4],
            #   "hitbox_type": "ghost", # phase through,
            #   "effect": "neg-gravity"
            # }

            curr_gridy = self.ground

            for obj in level_column:
                self.draw_obj(i-self.left, curr_gridy, obj['name'])

                # decrement curr_gridy
                curr_gridy -= 1

                if curr_gridy < -1: 
                    # move to next column if the vertical screen is full
                    # however, we render to y-pos -1 because some textures
                    # are larger than 1x1, such as portals
                    break

