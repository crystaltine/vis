import blessed
from typing import TYPE_CHECKING, List, Dict
from render.constants import CameraUtils
from render.utils import fcode, closest_quarter, len_no_ansi
from render.rect import PxRect
from logger import Logger
from math import floor, ceil
from render.TEXTURES import TEXTURES

if TYPE_CHECKING:
    from engine.objects import LevelObject

class Camera:    

    def __init__(self, leveldata: List[List['LevelObject']]):
        self.term = blessed.Terminal()
        self.left = 0 # start at 0. player starts at 10 (we get a nice padding)
        self.ground = ((CameraUtils.DEFAULT_GROUND_TOP_PERCENT * self.term.height) // 100) // CameraUtils.GRID_PX_Y
        """ Measured in blocks from the top of the screen. """
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

        obj_texture = TEXTURES.get(obj_name)
        
        terminal_pos = CameraUtils.grid_to_terminal_pos(x, y)
        
        for i in range(len(obj_texture)):

            # a clever way to not have to rerender the entire bg every time.
            # we cover up the entire texture after done
            refresh_optimization = fcode(background=TEXTURES.BG_COLOR) + " "*len(obj_texture[i])
            print(self.term.move_yx(round(terminal_pos[1]+i), round(terminal_pos[0])) + obj_texture[i] + refresh_optimization)

    def render_init(self):
        """
        Call this once. Draws the background and the floor, 
        which don't need to be updated every frame.
        """
        
        self.term.clear()

        ground_char_idx = self.ground*CameraUtils.GRID_PX_Y
        
        stuff = [
            PxRect(0, 0, self.term.width, ground_char_idx, self.term, TEXTURES.BG_COLOR), # bg
            PxRect(0, ground_char_idx, self.term.width, self.term.height, self.term, TEXTURES.GROUND_COLOR), # ground
        ]
        [item.render() for item in stuff]

    def render(self, player_pos: tuple):
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
        
        render starting from the ground-number of strips, so that the last strip is at ground level.
        
        ### Partial rendering
        
        we also need a system to draw half-blocks when they go off the screen. This allows
        much more draw resolution (since without rendering partial blocks each "pixel" becomes 4x2 chars.
        We want to be able to draw a block moving left using all the characters, not just 1/4 of them.
        
        Here's how we do this:
        
        at each frame we have a self.left. this is block-based, but SUPPORTS DECIMALS.
        we have to figure out which quarter it is closest to (.0, .25, .50, .75) and
        then offset each strip by 4* that amount of characters.
        
        For example, if the camera left is at 10.25, and we have a block at x=12,
        then we should render that block 7 characters (1.75 blocks) from the left,
        instead of 2 full blocks (8 characters).
        
        Thus, on each frame we must find the closest quarter, then delete the first 4* that amount of characters.
        Note that this will never remove more than a full block, which is consistent
        with our goal of only partially culling blocks that go off the screen.

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

        self.left = player_pos[0] - CameraUtils.CAMERA_LEFT_OFFSET

        all_strips = []

        for row in self.leveldata[-self.ground:]:
            render_strip_1 = fcode(background=TEXTURES.BG_COLOR) # start as the bg format code
            render_strip_2 = fcode(background=TEXTURES.BG_COLOR) # start as the bg format code
            
            if (floor(self.left)) >= len(row):
                continue # row is all behind us
            
            # TODO - add negative cam support or add an assert
            
            # FOR THE FIRST OBJECT (idx floor(self.left)):
            # we need to render this separately because it could be cut off by left side.
            # we render 4*nearest_quarter chars from the right side of its texture.
            # for example, if self.left = 0.21, nearest quarter is 0.25
            # another ex: if self.left = 1.0 exactly, then nearest quarter is 0.0
            # ^ in this case, a slice [0:] would render the entire texture, WHICH IS WHAT WE WANT.
            # and we only render the 2 rightmost chars of the texture.
            
            partial_render_offset = round(4 * closest_quarter(self.left))
            first_obj = row[floor(self.left)]
            
            # TODO - for now we just render some spaces (no texture)
            # for textures, we need a way to slice them while ignoring ANSI escape codes.
            
            #if first_obj is None:
                # 4 spaces to both strips(empty)
            empty_block = " "*(4-partial_render_offset)
            render_strip_1 += empty_block
            render_strip_2 += empty_block

            #else: 
            #    render_strip_1 += TEXTURES.get(first_obj["name"])[0][partial_render_offset:]
            #    render_strip_2 += TEXTURES.get(first_obj["name"])[1][partial_render_offset:]
                
            #Logger.log(f"[rendering leftmost obj]: self.left is {self.left}, partial_render_offset is {partial_render_offset}, idx is {floor(self.left)}")

            
            # render everything else fully
            # TODO - does right side work? blessed should handle overflow... maybe
            #Logger.log(f"rendering a row from {floor(self.left)+1} to {min(len(row), ceil(self.left + CameraUtils.screen_width_blocks(self.term)))}")
            for obj in row[floor(self.left)+1 : min(len(row), floor(self.left + CameraUtils.screen_width_blocks(self.term)))]:
                if obj.data is None:
                    # 4 spaces to both strips(empty)
                    empty_block = " "*CameraUtils.GRID_PX_X
                    render_strip_1 += empty_block
                    render_strip_2 += empty_block

                else: 
                    # TODO - (see docstring), this only works with 2-char tall textures
                    # we end off each texture with bg color so whitespace is not visible
                    render_strip_1 += TEXTURES.get(obj.data["name"])[1] + fcode(background=TEXTURES.BG_COLOR)
                    render_strip_2 += TEXTURES.get(obj.data["name"])[0] + fcode(background=TEXTURES.BG_COLOR)
            
            # @old (NVM IM BACK)-
            # make sure all strips are the char length of the terminal.
            # basically pad each one until they are at self.term.width
            # (!) had to bring this back to auto-erase the player texture as it moves
            render_strip_1 += " "*max(0, self.term.width-len_no_ansi(render_strip_1))
            render_strip_2 += " "*max(0, self.term.width-len_no_ansi(render_strip_2))
            
            # @new- (EXILED) only add a block's worth at the end. NOTE: this will break at low fps.
            # ^ however, this does save a lot of printing.
            # render_strip_1 += " "*CameraUtils.GRID_PX_X
            # render_strip_2 += " "*CameraUtils.GRID_PX_X

            # add to strips
            all_strips.append(render_strip_2)
            all_strips.append(render_strip_1)
        
        # draw every row starting from 0 to ground * block height
        # i know drawing the air is useless, but we need to cover up the player trail
        for i in range(self.ground*CameraUtils.GRID_PX_Y - len(all_strips)):
            print(self.term.move_yx(i, 0) + fcode(background=TEXTURES.BG_COLOR) + " "*self.term.width)
        
        # we keep track of this cuz we might skip an index, so it wont be matched
        row_in_terminal = (self.ground)*CameraUtils.GRID_PX_Y - len(all_strips)
        for i in range(len(all_strips)):
            # TODO - removed for now since just testing
            # if first strip and ground is odd, and strips reach all the way to the top, skip
            # if i == 0 and (self.ground % 2):
            #    continue
            
            print(self.term.move_yx(row_in_terminal, 0) + all_strips[i])
            row_in_terminal += 1
            
        # draw the player
        self.draw_player(player_pos[0], player_pos[1])

    def level_editor_render(self, cursor_pos: tuple, screen_pos: tuple, cur_cursor_obj):

        self.left = screen_pos[1] - CameraUtils.CAMERA_LEFT_OFFSET

        all_strips = []

        cursor_texture = fcode(background="#68FF06")

        cur_y = 0

        for row in self.leveldata[-self.ground:]:
            cur_x = 1

            render_strip_1 = fcode(background=TEXTURES.BG_COLOR) # start as the bg format code
            render_strip_2 = fcode(background=TEXTURES.BG_COLOR) # start as the bg format code
            
            if (floor(self.left)) >= len(row):
                continue # row is all behind us

            partial_render_offset = round(4 * closest_quarter(self.left))
            
            empty_block = " "*(4-partial_render_offset)
            render_strip_1 += empty_block
            render_strip_2 += empty_block
            
            for obj in row[floor(self.left)+1 : min(len(row), floor(self.left + CameraUtils.screen_width_blocks(self.term)))]:
                if cursor_pos[1] in {cur_y+1, cur_y-1, cur_y}:
                    if cursor_pos[0] in {cur_x+1, cur_x-1, cur_x}:
                        render_strips = self.draw_cursor((cur_x, cur_y), cursor_pos, cursor_texture, [render_strip_1, render_strip_2], obj, cur_cursor_obj)
                        render_strip_1 = render_strips[0]
                        render_strip_2 = render_strips[1]
                        cur_x += 1
                        continue
                if obj.data is None:
                    empty_block = " "*CameraUtils.GRID_PX_X
                    render_strip_1 += empty_block + fcode(background=TEXTURES.BG_COLOR)
                    render_strip_2 += empty_block + fcode(background=TEXTURES.BG_COLOR)

                else: 
                    render_strip_1 += TEXTURES.get(obj.data["name"])[1] + fcode(background=TEXTURES.BG_COLOR)
                    render_strip_2 += TEXTURES.get(obj.data["name"])[0] + fcode(background=TEXTURES.BG_COLOR)
                cur_x += 1
            
            render_strip_1 += " "*max(0, self.term.width-len_no_ansi(render_strip_1))
            render_strip_2 += " "*max(0, self.term.width-len_no_ansi(render_strip_2))

            all_strips.append(render_strip_2)
            all_strips.append(render_strip_1)
            cur_y += 1

        for i in range(self.ground*CameraUtils.GRID_PX_Y - len(all_strips)):
            print(self.term.move_yx(i, 0) + fcode(background=TEXTURES.BG_COLOR) + " "*self.term.width)

        row_in_terminal = (self.ground)*CameraUtils.GRID_PX_Y - len(all_strips)
        for i in range(len(all_strips)):

            print(self.term.move_yx(row_in_terminal, 0) + all_strips[i])
            row_in_terminal += 1
            
    def draw_player(self, player_x: float, player_y: float):
        """
        Draws the player at the specified position.
        The player is 1 block by 1 block for cube mode (the only mode rn)
        """
        
        # offset to ground level
        player_topmost_y = round((self.ground-player_y-1) * CameraUtils.GRID_PX_Y)
        
        # camera has a bit of left padding
        camera_offset_chars = CameraUtils.GRID_PX_X * CameraUtils.CAMERA_LEFT_OFFSET
        
        for i in range(len(TEXTURES.PLAYER_ICON)):
            print(self.term.move_yx(player_topmost_y+i, camera_offset_chars) + TEXTURES.PLAYER_ICON[i])

    def draw_cursor(self, cur_pos: tuple, cursor_pos: tuple, cursor_texture, render_strips: list, obj, cur_cursor_obj):
        if obj.data is not None and (obj.data["name"].find("orb") != -1 or obj.data["name"].find("block") != -1):
            render_strips[1] += TEXTURES.get(obj.data["name"])[0] + fcode(background=TEXTURES.BG_COLOR)
            render_strips[0] += TEXTURES.get(obj.data["name"])[1] + fcode(background=TEXTURES.BG_COLOR)
            return render_strips
        if cur_pos[1] == cursor_pos[1]:
            layer = (True, True)
        elif cur_pos[1]-1 == cursor_pos[1]:
            layer = (False, True)
        elif cur_pos[1]+1 == cursor_pos[1]:
            layer = (True, False)
        if cur_pos[0] == cursor_pos[0]:
            if layer == (True, True) and cur_cursor_obj != None:
                if cur_cursor_obj.data["name"].find("orb") != -1 or cur_cursor_obj.data["name"].find("block") != -1:
                    render_strips[1] += TEXTURES.get(cur_cursor_obj.data["name"])[0] + fcode(background=TEXTURES.BG_COLOR)
                    render_strips[0] += TEXTURES.get(cur_cursor_obj.data["name"])[1] + fcode(background=TEXTURES.BG_COLOR)
                else:
                    render_strips = self.draw_center(render_strips, cursor_texture, layer, cur_cursor_obj)
            else:
                render_strips = self.draw_center(render_strips, cursor_texture, layer, obj)
        elif cur_pos[0]-1 == cursor_pos[0]:
            render_strips = self.draw_r_edge(render_strips, cursor_texture, layer, obj)
        elif cur_pos[0]+1 == cursor_pos[0]:
            render_strips = self.draw_l_edge(render_strips, cursor_texture, layer, obj)
        return render_strips

    def draw_center(self, render_strips, cursor_texture, layer, obj):
        empty_block = " "*CameraUtils.GRID_PX_X
        if obj.data is None:
            if layer[1]:
                render_strips[1] += cursor_texture + empty_block
            else:
                render_strips[1] += empty_block
            if layer[0]:
                render_strips[0] += cursor_texture + empty_block
            else:
                render_strips[0] += empty_block
        else:
            if layer[1]:
                render_strips[1] += cursor_texture + TEXTURES.get_raw_obj_text(obj.data["name"])[0]
            else:
                render_strips[1] += TEXTURES.get_raw_obj_text(obj.data["name"])[0]
            if layer[0]:
                render_strips[0] += cursor_texture + TEXTURES.get_raw_obj_text(obj.data["name"])[1]
            else:
                render_strips[0] += TEXTURES.get_raw_obj_text(obj.data["name"])[1]
        return render_strips
    
    def draw_l_edge(self, render_strips, cursor_texture, layer, obj):
        empty_block = " "*(CameraUtils.GRID_PX_X//2)
        if obj.data is None:
            if layer[1]:
                render_strips[1] += empty_block + cursor_texture + empty_block
            else:
                render_strips[1] += empty_block + fcode(background=TEXTURES.BG_COLOR) + empty_block
            if layer[0]:
                render_strips[0] += empty_block + cursor_texture + empty_block
            else:
                render_strips[0] += empty_block + fcode(background=TEXTURES.BG_COLOR) + empty_block
        else:
            top = TEXTURES.get_raw_obj_text(obj.data["name"])[1]
            bottom = TEXTURES.get_raw_obj_text(obj.data["name"])[0]
            if layer[1]:
                render_strips[1] += bottom[len(bottom) - 4:len(bottom) - 2] + cursor_texture + bottom[len(bottom) - 2:]
            else:
                render_strips[1] += bottom
            if layer[0]:
                render_strips[0] += top[len(top) - 4:len(top) - 2] + cursor_texture + top[len(top) - 2:]
            else:
                render_strips[0] += top
        return render_strips
    
    def draw_r_edge(self, render_strips, cursor_texture,layer, obj):
        empty_block = " "*(CameraUtils.GRID_PX_X//2)
        if obj.data is None:
            if layer[1]:
                render_strips[1] += cursor_texture + empty_block + fcode(background=TEXTURES.BG_COLOR) + empty_block
            else:
                render_strips[1] += empty_block + fcode(background=TEXTURES.BG_COLOR) + empty_block
            if layer[0]:
                render_strips[0] += cursor_texture + empty_block + fcode(background=TEXTURES.BG_COLOR) + empty_block
            else:
                render_strips[0] += empty_block + fcode(background=TEXTURES.BG_COLOR) + empty_block
        else:
            top = TEXTURES.get_raw_obj_text(obj.data["name"])[1]
            bottom = TEXTURES.get_raw_obj_text(obj.data["name"])[0]
            if layer[1]:
                render_strips[1] += cursor_texture + bottom[len(bottom) - 4:len(bottom) - 2] + fcode(background=TEXTURES.BG_COLOR) + bottom[len(bottom) - 2:]
            else:
                render_strips[1] += bottom
            if layer[0]:
                render_strips[0] += cursor_texture + top[len(top) - 4:len(top) - 2] + fcode(background=TEXTURES.BG_COLOR) + top[len(top) - 2:]
            else:
                render_strips[0] += top
        return render_strips
    