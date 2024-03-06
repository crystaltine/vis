import blessed
from typing import TYPE_CHECKING, List, Dict
from render.constants import CameraUtils
from render.utils import fcode
from render.rect import Rect
from logger import Logger
from math import floor, ceil

class Camera:

    BG_COLOR = "#287DFF"
    GROUND_COLOR = "#0066ff"
    BLOCK_COLOR_1 = "#444"
    BLOCK_COLOR_2 = "#555"

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

    def __init__(self, leveldata: List[List[Dict]]):
        self.term = blessed.Terminal()
        self.left = -CameraUtils.CAMERA_LEFT_OFFSET # since player starts at 0
        self.ground = CameraUtils.DEFAULT_GROUND_LEVEL
        self.leveldata = leveldata

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
        
        terminal_pos = CameraUtils.grid_to_terminal_pos(x, y)
        
        for i in range(len(obj_texture)):

            # a clever way to not have to rerender the entire bg every time.
            # we cover up the entire texture after done
            refresh_optimization = fcode(background=Camera.BG_COLOR) + " "*len(obj_texture[i])
            print(self.term.move_yx(round(terminal_pos[1]+i), round(terminal_pos[0])) + obj_texture[i] + refresh_optimization)

    def render_init(self):
        """
        Call this once. Draws the background and the floor, 
        which don't need to be updated every frame.
        """
        
        self.term.clear()

        ground_percent = (100*self.ground*CameraUtils.GRID_PX_Y)//self.term.height

        stuff = [
            Rect(0, 0, 100, 100, self.term, Camera.BG_COLOR), # bg
            Rect(0, ground_percent, 100, 100, self.term, Camera.GROUND_COLOR), # ground
        ]
        [item.render() for item in stuff]

    def render(self, player_x: float):
        """
        Renders a frame onto the screen.

        ## Drawing algorithm:
        To optimize rendering, we need to break up the screen into horiz. strips of 1 character.
        Levels are defined by a list of rows, starting from top down, then left->right
        @TODO - for now, we assume all textures are 4row x 2col

        This means each block row will have 2 strips to render.

        Also, we only need to render the indices that are in camera.
        We should only load from:
            max(0, camera_left) to 
            min(row length, camera_left + screen_block_width)

        also do y-culling to make the frame fit the screen
        the first strip of the ground is drawn at row self.ground
        thus, there are self.ground strips to render.
        
        for example, if ground=14, then we have to render 14 strips of the level
        which would be 7 blocks. So we pick the last 7 lists in leveldata.
        This can be defined by the slice `[-7:]`. general: `[-self.ground//2:]`
        (note that int div rounds down for x<0, thus -17//2 == -9 which is perfect)

        if ground is odd, round the div/2 up. e.g. ground=15 -> render 8 rows.
        ^ HOWEVER, we must skip the first render strip in this case, since otherwise 
        we would go below the ground. So when we render all the strips, check if
        self.ground is odd. if it is, skip first strip.

        ### pseudocode

        ```
        all_strips = []

        for each grid row[-self.ground//2:]:
            render_strip_1 = ""
            render_strip_2 = ""

            for obj in row[max(0, camera_left) to min(row length, camera_left + screen_block_width)]

                if obj is none:
                    strip += "    " (4 spaces) to both strips

                render_strip_1 += top half of obj texture
                render_strip_2 += bottom half of obj texture
        
        then just draw all the strips


        ```
        Sets `self.left` to `player_x - CameraUtils.CAMERA_LEFT_OFFSET`
        to make it so that the player is kinda sorta near the center of the screen
        """

        self.left = player_x - CameraUtils.CAMERA_LEFT_OFFSET

        all_strips = []

        for row in self.leveldata[-self.ground//2:]:
            render_strip_1 = ""
            render_strip_2 = ""

            for obj in row[max(0, floor(self.left)) : min(len(row), self.left + ceil(CameraUtils.screen_width_blocks(self.term)))]:
                if obj is None:
                    # 4 spaces to both strips(empty)
                    empty_block = fcode(background=Camera.BG_COLOR) + " "*CameraUtils.GRID_PX_X
                    render_strip_1 += empty_block
                    render_strip_2 += empty_block

                else: 
                    # TODO - (see docstring), this only works with 2-char tall textures
                    render_strip_1 += Camera.TEXTURES[obj["name"]][0]
                    render_strip_2 += Camera.TEXTURES[obj["name"]][1]
            
            # make sure all strips are the char length of the terminal.
            # basically pad each one until they are at self.term.width

            render_strip_1 += fcode(background=Camera.BG_COLOR) + " "*max(0, self.term.width-len(render_strip_1))
            render_strip_2 += fcode(background=Camera.BG_COLOR) + " "*max(0, self.term.width-len(render_strip_2))

            # add to strips
            all_strips.append(render_strip_1)
            all_strips.append(render_strip_2)
        
        Logger.log(f"[Renderer]: ground@{self.ground}, all_strips len=${len(all_strips)}")
        
        # we keep track of this cuz we might skip an index, so it wont be matched
        row_in_terminal = self.ground*CameraUtils.GRID_PX_Y - len(all_strips)
        for i in range(len(all_strips)):
            # if first strip and ground is odd, skip
            if i == 0 and (self.ground % 2):
                continue
            
            print(self.term.move_yx(row_in_terminal, 0) + all_strips[i])
            row_in_terminal += 1