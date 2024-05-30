import blessed
from typing import TYPE_CHECKING, List
from render.constants import CameraUtils
from render.utils import fcode, closest_quarter, len_no_ansi
from logger import Logger
from math import floor, ceil
import traceback
from render.texture_manager import TextureManager
from render.camera_frame import CameraFrame
from bottom_menu import draw_text

if TYPE_CHECKING:
    from engine.objects import LevelObject
    from game import Game

class Camera:
    """
    Handles general rendering of the game.
    """

    def __init__(self, leveldata: List[List['LevelObject']]):
        self.term = blessed.Terminal()
        
        self.px_height = self.term.height*2
        """ height of the screen in PIXELS, equal to 2*terminal height """
        self.px_width = self.term.width
        """ width of the screen in PIXELS, equal to terminal width """
        
        self.leveldata = leveldata
        self.curr_frame: CameraFrame = None
        
        self.camera_left: float = 0 # start at 0. player starts at 10 (we get a nice padding)
        """ Measured in blocks from the beginning of the level. """
        self.camera_bottom: float = -CameraUtils.GROUND_HEIGHT
        """ Measured in blocks from the bottom (lowermost row) of the level. """
        
        self.player_y_info = {
            "physics_pos": 0, # assume default TODO - maybe give Camera access to the player object?
            "screen_pos": self.px_height - CameraUtils.GROUND_HEIGHT*CameraUtils.BLOCK_HEIGHT - CameraUtils.BLOCK_HEIGHT
        }
        """ dict{
                "screen_pos": (px) How far from the top of the screen the player should be rendered.
                "physics_pos": The player's physics y-position for which the above value was calculated
            }
        """

    def update_camera_y_pos(self, player_pos: tuple) -> None:
        """
        Handles reposition checking for the camera so that the player doesn't go off screen.
        
        ### Notes (values as of 1:30AM, May 28, 2024)
        The player icon should always be in the middle 50% of the screen (never in the top 25% or bottom 25%).
        we are assuming large but not too large screen size here (24px is not less than 25% or more than 75% of the screen)
        
        If we detect a change in player-y from the last recorded player-y that would bring the player icon out of the middle 50%,
        then we move the camera position up
        
        Also note that player_pos[1] is player y, and it represents the BOTTOM of the player (so we have to offset by 1 to get player top)
        """
        
        min_acceptable_y = CameraUtils.MIN_PLAYER_SCREEN_OFFSET * self.px_height
        max_acceptable_y = CameraUtils.MAX_PLAYER_SCREEN_OFFSET * self.px_height
        
        # find delta from most recent physics pos
        delta_y = player_pos[1] - self.player_y_info["physics_pos"]
        delta_y_px = delta_y * CameraUtils.BLOCK_HEIGHT
        
        # if adding that would bring us over the 75% mark, then we need to adjust the ground down,
        # and keep the player rendered at 75% up the screen
        
        # otherwise, simply update the player_y_info field and move on (ground wont change)
        
        new_player_screen_pos = self.player_y_info["screen_pos"] - delta_y_px
        
        # check player going too high up on the screen
        if new_player_screen_pos < min_acceptable_y:
            # move the camera up by the amount that we went over
            self.camera_bottom += (min_acceptable_y - new_player_screen_pos) / CameraUtils.BLOCK_HEIGHT
            self.player_y_info["screen_pos"] = self.px_height - CameraUtils.BLOCK_HEIGHT*(player_pos[1] + 1 - self.camera_bottom)
            self.player_y_info["physics_pos"] = player_pos[1]
        
        # check player going too low on the screen
        elif new_player_screen_pos > max_acceptable_y:
            # move the camera down by the amount that we went over
            self.camera_bottom -= (new_player_screen_pos - max_acceptable_y) / CameraUtils.BLOCK_HEIGHT
            self.player_y_info["screen_pos"] = self.px_height - CameraUtils.BLOCK_HEIGHT*(player_pos[1] + 1 - self.camera_bottom)
            self.player_y_info["physics_pos"] = player_pos[1]
            
        # else, we are in the middle 50% of the screen, so just update the player_y_info field
        else:
            self.player_y_info["screen_pos"] = new_player_screen_pos
            self.player_y_info["physics_pos"] = player_pos[1]            

    def get_screen_coordinates(self, obj_x: int, obj_y: int) -> tuple:
        """
        Returns the screen coordinates for the given object, in (x,y),
        where x is the number of pixels from the left of the screen, and 
        is the number of pixels from the top of the screen.
        
        `obj_x` and `obj_y` are the physics coordinates of the object (in blocks).
        """
        screen_x = round((obj_x - self.camera_left) * CameraUtils.BLOCK_WIDTH)
        screen_y = self.px_height - round((obj_y - self.camera_bottom) * CameraUtils.BLOCK_HEIGHT)
        
        Logger.log(f"[Camera/get_screen_coordinates] obj_x,y={obj_x},{obj_y}, camera_left,bottom={self.camera_left},{self.camera_bottom} => screen_x,y={screen_x},{screen_y}")
        
        return screen_x, screen_y

    def render_init(self) -> None:
        """
        New rendering algorithm that uses CameraFrames instead of just characters.
        Initializes the frame with the background color, and sets self.curr_frame for the first time.
        """
        self.curr_frame = CameraFrame(self.term)
        self.curr_frame.fill(TextureManager.bg_color)
        self.curr_frame.render_raw()

    def render(self, game: "Game") -> None:
        """
        Renders a new frame based on where the player is.
        Handles ground/camera repositioning, etc.
        Optimized to compare the newly constructed frame with the last rendered frame, 
        and to only redraw the differences.
        """
        
        if game.is_crashed:
            # if crashed, don't render anything
            return
        
        new_frame = CameraFrame(self.term)
        new_frame.fill(TextureManager.bg_color)
        
        # move camera to player
        self.update_camera_y_pos(game.player.pos)
        self.camera_left = game.player.pos[0] - CameraUtils.CAMERA_LEFT_OFFSET
        camera_right = self.camera_left + CameraUtils.screen_width_blocks(self.term)
        camera_top = self.camera_bottom + CameraUtils.screen_height_blocks(self.term)

        visible_vert_range = floor(self.camera_bottom), 1+ceil(self.camera_bottom + CameraUtils.screen_height_blocks(self.term))
        # this should be smth like (5, 12) which is the range of y-pos of the grid that is visible on the screen
        
        visible_vert_slice = slice(
            max(0, len(self.leveldata)-visible_vert_range[1]+1),
            min(len(self.leveldata), len(self.leveldata)-visible_vert_range[0]+1)
        ) # slice object for the rows of self.leveldata to use. Prints top to bottom.

        # y-pos on screen (in pixels) to render the next row at.
        # increment by block_height_px after each row.
        # start at term_height_px - ground_height_px - number of rows to render * block_height_px
        curr_screen_y_pos = self.px_height - CameraUtils.GROUND_HEIGHT*CameraUtils.BLOCK_HEIGHT - (visible_vert_slice.stop-visible_vert_slice.start)*CameraUtils.BLOCK_HEIGHT

        #Logger.log(f"[Camera/render] visible_vert_slice = {visible_vert_slice}, initial curr_screen_y_pos = {curr_screen_y_pos}")

        for row in self.leveldata[visible_vert_slice]:      
            # horizontal range of grid cells that are in the camera range. Includes any partially visible cells on the sides.
            visible_horiz_range = (max(0, floor(self.camera_left)), min(len(row), ceil(camera_right))) # last index is exclusive

            #Logger.log(f"[Camera/render] {self.camera_left=}, player-x={player_pos[0]}, {visible_horiz_range=}")

            # add textures of all the objects in the row to the frame
            for obj in row[visible_horiz_range[0]:visible_horiz_range[1]]:
                if obj.data is not None:
                    xpos_on_screen = round((obj.x - self.camera_left) * CameraUtils.BLOCK_WIDTH)
                    #try:
                    #Logger.log(f"[Camera/render] adding texture {obj.data['name']} at {xpos_on_screen}, {curr_screen_y_pos}, screen w,h = {self.px_width}, {self.px_height}")
                    #Logger.log(f"^^ obtained x_pos_on_screen: {xpos_on_screen} by doing round(({obj.x} - {self.camera_left}) * {CameraUtils.BLOCK_WIDTH})")
                    #Logger.log(f"^^ Meanwhile, the player's screen pos is {self.player_y_info['screen_pos']}")
                    #Logger.log(f"the obj's physics x-pos is {obj.x}, cam_left={self.camera_left}, player_x={player_pos[0]}")
                    new_frame.add_pixels_topleft(xpos_on_screen, curr_screen_y_pos, TextureManager.textures.get(obj.data["name"]))
                    #except Exception as e:
                    #    Logger.log(f"error: {traceback.format_exc()}")
                    
            curr_screen_y_pos += CameraUtils.BLOCK_HEIGHT
        
        
        #Logger.log(f"[Camera/render] camera_top: {camera_top:2f}, camera_bottom: {self.camera_bottom:2f}")
        #Logger.log(f"slice: {visible_vert_slice}, range: {visible_vert_range}")
        
        # draw ground. The top of the ground ground should be at physics y=0.
        ground_screen_y_pos = camera_top * CameraUtils.BLOCK_HEIGHT
        new_frame.add_pixels_topleft(0, ground_screen_y_pos, TextureManager.textures.get("ground"))

        # draw player
        player_xpos_on_screen = CameraUtils.CAMERA_LEFT_OFFSET * CameraUtils.BLOCK_WIDTH
        new_frame.add_pixels_topleft(player_xpos_on_screen, self.player_y_info['screen_pos'], TextureManager.player_icons[game.player.get_animation_frame_index()])
        
        # draw attempt number
        self.draw_attempt(new_frame, game.player.ORIGINAL_START_POS[0], game.attempt_number) # draw the attempt number
        
        # draw any checkpoints TODO - render multiple checkpoints, OOP-ize practice mode?
        if game.last_checkpoint:
            self.draw_checkpoint(new_frame, game.last_checkpoint[0], game.last_checkpoint[1])
        
        # render the new frame
        new_frame.render(self.curr_frame)
        self.curr_frame = new_frame

    def level_editor_render(self, cursor_pos: tuple, screen_pos: tuple, cur_cursor_obj):

        self.camera_left = screen_pos[0] - CameraUtils.CAMERA_LEFT_OFFSET

        all_strips = []

        cursor_texture = fcode(background="#68FF06")

        cur_y = 0

        for row in self.leveldata[-self.ground:]:
            cur_x = 1

            render_strip_1 = fcode(background=TextureManager.bg_color) # start as the bg format code
            render_strip_2 = fcode(background=TextureManager.bg_color) # start as the bg format code
            
            if (floor(self.camera_left)) >= len(row):
                continue # row is all behind us

            partial_render_offset = round(4 * closest_quarter(self.camera_left))
            
            empty_block = " "*(4-partial_render_offset)
            render_strip_1 += empty_block
            render_strip_2 += empty_block
            
            for obj in row[floor(self.camera_left)+1 : min(len(row), floor(self.camera_left + CameraUtils.screen_width_blocks(self.term)))]:
                if cursor_pos[1] in {cur_y+1, cur_y-1, cur_y}:
                    if cursor_pos[0] in {cur_x+1, cur_x-1, cur_x}:
                        render_strips = self.draw_cursor((cur_x, cur_y), cursor_pos, cursor_texture, [render_strip_1, render_strip_2], obj, cur_cursor_obj)
                        render_strip_1 = render_strips[0]
                        render_strip_2 = render_strips[1]
                        cur_x += 1
                        continue
                if obj.data is None:
                    empty_block = " "*CameraUtils.BLOCK_WIDTH
                    render_strip_1 += empty_block + fcode(background=TextureManager.bg_color)
                    render_strip_2 += empty_block + fcode(background=TextureManager.bg_color)

                else: 
                    render_strip_1 += TextureManager.get_texture(obj.data["name"])()[1] + fcode(background=TextureManager.bg_color)
                    render_strip_2 += TextureManager.get_texture(obj.data["name"])()[0] + fcode(background=TextureManager.bg_color)
                cur_x += 1
            
            render_strip_1 += " "*max(0, self.term.width-len_no_ansi(render_strip_1))
            render_strip_2 += " "*max(0, self.term.width-len_no_ansi(render_strip_2))

            all_strips.append(render_strip_2)
            all_strips.append(render_strip_1)
            cur_y += 1

        for i in range(self.ground*CameraUtils.BLOCK_HEIGHT - len(all_strips)):
            print(self.term.move_yx(i, 0) + fcode(background=TextureManager.bg_color) + " "*self.term.width)

        row_in_terminal = (self.ground)*CameraUtils.BLOCK_HEIGHT - len(all_strips)
        for i in range(len(all_strips)):

            print(self.term.move_yx(row_in_terminal, 0) + all_strips[i])
            row_in_terminal += 1

    def draw_checkpoint(self, frame: CameraFrame, x: float, y: float) -> None:
        """
        Draws a checkpoint at the specified position relative to the given player position.
        Args:
            x (float): The x-coordinate of the checkpoint.
            y (float): The y-coordinate of the checkpoint.
        """

        pos_on_screen = self.get_screen_coordinates(x, y)
        frame.add_pixels_topleft(*pos_on_screen, TextureManager.get_texture("checkpoint")())
        
    def draw_attempt(self, frame: CameraFrame, player_initial_x: float, attempt: int) -> None:
        """
        Draws the attempt number when the player spawns in.
        Args:
            player_initial_x (float): The initial x-coordinate of the player when the game began.
            attempt (int): The current attempt number to be displayed.
        """

        # Set coordinates for drawing the attempt text
        # (setting the x coordinate to the coordinate the player spawned in at)
        x = player_initial_x
        y = 10
        
        pos_on_screen = self.get_screen_coordinates(x, y)
        
        frame.add_text_centered_at(*pos_on_screen, TextureManager.font_small1, f"Attempt {attempt}")

        # Calculate player's topmost y-coordinate for positioning text
        #player_topmost_y = round((self.ground - y - 1) * CameraUtils.GRID_PX_Y)
        ## offset x coordinate of drawing by where the player is on the screen
        #offset = round(player_x - x + 1)
        #camera_offset_chars = CameraUtils.GRID_PX_X * (CameraUtils.CAMERA_LEFT_OFFSET - offset // 2)
#
        ## Draw the attempt text if it's within the camera's view
        #if camera_offset_chars > 0:
        #    draw_text(f"Attempt: {attempt}", camera_offset_chars, player_topmost_y, bg_color="#007eff")

    def draw_cursor(self, cur_pos: tuple, cursor_pos: tuple, cursor_texture, render_strips: list, obj, cur_cursor_obj):
        if obj.data is not None and (obj.data["name"].find("orb") != -1 or obj.data["name"].find("block") != -1):
            render_strips[1] += TextureManager.get_texture(obj.data["name"])()[0] + fcode(background=TextureManager.bg_color)
            render_strips[0] += TextureManager.get_texture(obj.data["name"])()[1] + fcode(background=TextureManager.bg_color)
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
                    render_strips[1] += TextureManager.get_texture(cur_cursor_obj.data["name"])()[0] + fcode(background=TextureManager.bg_color)
                    render_strips[0] += TextureManager.get_texture(cur_cursor_obj.data["name"])()[1] + fcode(background=TextureManager.bg_color)
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
        empty_block = " "*CameraUtils.BLOCK_WIDTH
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
                render_strips[1] += cursor_texture + TextureManager.get_raw_obj_text(obj.data["name"])[0]
            else:
                render_strips[1] += TextureManager.get_raw_obj_text(obj.data["name"])[0]
            if layer[0]:
                render_strips[0] += cursor_texture + TextureManager.get_raw_obj_text(obj.data["name"])[1]
            else:
                render_strips[0] += TextureManager.get_raw_obj_text(obj.data["name"])[1]
        return render_strips
    
    def draw_l_edge(self, render_strips, cursor_texture, layer, obj):
        empty_block = " "*(CameraUtils.BLOCK_WIDTH//2)
        if obj.data is None:
            if layer[1]:
                render_strips[1] += empty_block + cursor_texture + empty_block
            else:
                render_strips[1] += empty_block + fcode(background=TextureManager.bg_color) + empty_block
            if layer[0]:
                render_strips[0] += empty_block + cursor_texture + empty_block
            else:
                render_strips[0] += empty_block + fcode(background=TextureManager.bg_color) + empty_block
        else:
            top = TextureManager.get_raw_obj_text(obj.data["name"])[1]
            bottom = TextureManager.get_raw_obj_text(obj.data["name"])[0]
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
        empty_block = " "*(CameraUtils.BLOCK_WIDTH//2)
        if obj.data is None:
            if layer[1]:
                render_strips[1] += cursor_texture + empty_block + fcode(background=TextureManager.bg_color) + empty_block
            else:
                render_strips[1] += empty_block + fcode(background=TextureManager.bg_color) + empty_block
            if layer[0]:
                render_strips[0] += cursor_texture + empty_block + fcode(background=TextureManager.bg_color) + empty_block
            else:
                render_strips[0] += empty_block + fcode(background=TextureManager.bg_color) + empty_block
        else:
            top = TextureManager.get_raw_obj_text(obj.data["name"])[1]
            bottom = TextureManager.get_raw_obj_text(obj.data["name"])[0]
            if layer[1]:
                render_strips[1] += cursor_texture + bottom[len(bottom) - 4:len(bottom) - 2] + fcode(background=TextureManager.bg_color) + bottom[len(bottom) - 2:]
            else:
                render_strips[1] += bottom
            if layer[0]:
                render_strips[0] += cursor_texture + top[len(top) - 4:len(top) - 2] + fcode(background=TextureManager.bg_color) + top[len(top) - 2:]
            else:
                render_strips[0] += top
        return render_strips
    