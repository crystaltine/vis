import blessed
from typing import TYPE_CHECKING, List, Tuple
from math import floor, ceil
import traceback

from logger import Logger
from render.constants import CameraConstants
from engine.constants import EngineConstants
from render.utils import fcode, closest_quarter, len_no_ansi
from render.texture_manager import TextureManager
from render.camera_frame import CameraFrame
from gd_constants import GDConstants
from skimage.draw import line_aa
from engine.player import Player

if TYPE_CHECKING:
    from level import LevelObject, Level
    from game import Game

class Camera:
    """
    Handles general rendering of the game.
    """

    def __init__(self, level: "Level"):
        
        self.px_height = GDConstants.term.height*2
        """ height of the screen in PIXELS, equal to 2*terminal height """
        self.px_width = GDConstants.term.width
        """ width of the screen in PIXELS, equal to terminal width """
        
        self.level = level
        self.curr_frame: CameraFrame = None
        
        self.camera_left: float = 0 # start at 0. player starts at 10 (we get a nice padding)
        """ Measured in blocks from the beginning of the level. """
        self.camera_bottom: float = -CameraConstants.GROUND_HEIGHT
        """ Measured in blocks from the bottom (lowermost row) of the level. """
        
        self.player_y_info = {
            "physics_pos": level.metadata.get("start_settings").get("position")[1], # start at player's initial y (bottom of player icon)
            "screen_pos": self.px_height - CameraConstants.GROUND_HEIGHT*CameraConstants.BLOCK_HEIGHT - CameraConstants.BLOCK_HEIGHT
        }
        """ 
        dict{
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
        
        min_acceptable_y = CameraConstants.MIN_PLAYER_SCREEN_OFFSET * self.px_height
        max_acceptable_y = CameraConstants.MAX_PLAYER_SCREEN_OFFSET * self.px_height
        
        # find delta from most recent physics pos
        delta_y = player_pos[1] - self.player_y_info["physics_pos"]
        #Logger.log(f"update pos: delta_y = {delta_y} = {player_pos[1]} - {self.player_y_info["physics_pos"]}")
        delta_y_px = delta_y * CameraConstants.BLOCK_HEIGHT
        
        # if adding that would bring us over the 75% mark, then we need to adjust the ground down,
        # and keep the player rendered at 75% up the screen
        
        # otherwise, simply update the player_y_info field and move on (ground wont change)
        
        new_player_screen_pos = self.player_y_info["screen_pos"] - delta_y_px
        
        # check player going too high up on the screen
        if new_player_screen_pos < min_acceptable_y:
            # move the camera up by the amount that we went over
            self.camera_bottom += (min_acceptable_y - new_player_screen_pos) / CameraConstants.BLOCK_HEIGHT
            self.player_y_info["screen_pos"] = self.px_height - CameraConstants.BLOCK_HEIGHT*(player_pos[1] + 1 - self.camera_bottom)
            self.player_y_info["physics_pos"] = player_pos[1]
        
        # check player going too low on the screen
        elif new_player_screen_pos > max_acceptable_y:
            # move the camera down by the amount that we went over
            self.camera_bottom -= (new_player_screen_pos - max_acceptable_y) / CameraConstants.BLOCK_HEIGHT
            self.player_y_info["screen_pos"] = self.px_height - CameraConstants.BLOCK_HEIGHT*(player_pos[1] + 1 - self.camera_bottom)
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
        screen_x = round((obj_x - self.camera_left) * CameraConstants.BLOCK_WIDTH)
        screen_y = self.px_height - round((obj_y - self.camera_bottom) * CameraConstants.BLOCK_HEIGHT)
        
        return screen_x, screen_y

    def render_init(self) -> None:
        """ Initializes the screen with the background color, and sets self.curr_frame for the first time. """
        self.curr_frame = CameraFrame()
        self.curr_frame.fill(self.level.bg_color)
        self.curr_frame.render_raw()

    def render(self, game: "Game", render_raw = False) -> None:
        """
        Renders a new frame based on where the player is.
        Handles ground/camera repositioning, etc.
        Optimized to compare the newly constructed frame with the last rendered frame, 
        and to only redraw the differences.
        """
        
        if game.is_crashed:
            # if crashed, don't render anything
            return
        
        new_frame = CameraFrame()
        new_frame.fill(self.level.bg_color)
        
        # move camera to player
        #Logger.log(f"[1] screen pos for playher: {self.player_y_info['screen_pos']}")
        self.update_camera_y_pos(game.player.pos)
        #Logger.log(f"[2] screen pos for playher: {self.player_y_info['screen_pos']}")
        self.camera_left = game.player.pos[0] - CameraConstants.CAMERA_LEFT_OFFSET
        camera_right = self.camera_left + CameraConstants.screen_width_blocks()
        camera_top = self.camera_bottom + CameraConstants.screen_height_blocks()

        #Logger.log(f"[Camera/render] {self.camera_bottom=:2f}, {self.player_y_info['screen_pos']=:4f}, {game.player.pos=}")

        visible_vert_range = max(0, floor(self.camera_bottom)), min(self.level.height, 1+ceil(self.camera_bottom + CameraConstants.screen_height_blocks()))
        # this should be smth like (5, 12) which is the range of y-pos of the grid that is visible on the screen. Exclusive of the second number.

        # first calc where the ground would be rendered
        ground_screen_y_pos = camera_top * CameraConstants.BLOCK_HEIGHT
        
        # we start rendering the row at ground - (y+1)*block_height, and decrement by block_height after each row
        curr_screen_y_pos = ground_screen_y_pos - CameraConstants.BLOCK_HEIGHT*(1+visible_vert_range[0])

        #Logger.log(f"[Camera/render] visible_vert_slice = {visible_vert_slice}, initial curr_screen_y_pos = {curr_screen_y_pos}")
        for row in range(*visible_vert_range):
            # horizontal range of grid cells that are in the camera range. Includes any partially visible cells on the sides.
            visible_horiz_range = (max(0, floor(self.camera_left)), min(self.level.length, ceil(camera_right))) # last index is exclusive

            #Logger.log(f"[Camera/render] {self.camera_left=}, {row=}, {curr_screen_y_pos=}, player@{game.player.pos=}, {visible_horiz_range=}, {visible_vert_range=}")

            # add textures of all the visible objects in this row to the new frame
            for obj in self.level.get_row(row, *visible_horiz_range):
                if obj is not None:
                    
                    #Logger.log(f"NotNone obj!!!! {obj} @ {obj.x, obj.y}")
                    
                    # calculate where it will truly be rendered on the screen
                    xpos_on_screen = round((obj.x - self.camera_left) * CameraConstants.BLOCK_WIDTH)
                    ypos_on_screen = curr_screen_y_pos
                    
                    # convert from topleft to center
                    xpos_on_screen += CameraConstants.BLOCK_WIDTH // 2
                    ypos_on_screen += CameraConstants.BLOCK_HEIGHT // 2
                    
                    # get transformed texture, with rotations, color, etc. (attempts to use cache for optimization)
                    obj_texture = TextureManager.get_transformed_texture(self.level, obj, hide_invis=True)
                    
                    #Logger.log(f"[LevelEditor/render_main_editor] Adding texture w shape={obj_texture.shape} @ {xpos_on_screen, ypos_on_screen}")
                    new_frame.add_pixels_centered_at(xpos_on_screen, round(ypos_on_screen), obj_texture)
                    
            curr_screen_y_pos -= CameraConstants.BLOCK_HEIGHT
        
        
        #Logger.log(f"[Camera/render] camera_top: {camera_top:2f}, camera_bottom: {self.camera_bottom:2f}")
        #Logger.log(f"slice: {visible_vert_slice}, range: {visible_vert_range}")
        
        # draw ground. The top of the ground ground should be at physics y=0.
        # TODO - make ground recolorable/move
        new_frame.add_pixels_topleft(0, ground_screen_y_pos, TextureManager.get_curr_ground_texture(self.level, game.player.get_dist_from_start()))

        # draw player
        player_xpos_on_screen = CameraConstants.CAMERA_LEFT_OFFSET * CameraConstants.BLOCK_WIDTH
        new_frame.add_pixels_topleft(round(player_xpos_on_screen), round(self.player_y_info['screen_pos']), TextureManager.get_curr_player_icon(game.player))
        
        # draw attempt number
        self.draw_attempt(new_frame, game.player.ORIGINAL_START_POS[0], game.attempt_number) # draw the attempt number
        
        # draw wave trail
        if game.player.gamemode == "wave":
            self.render_wave_trail(new_frame, game)
        
        # draw progress bar
        self.render_progress_bar(new_frame, game.get_progress_percentage())
        
        # draw any checkpoints TODO - render multiple checkpoints, OOP-ize practice mode?
        # draw most recent checkpoint if the game is in practice mode and has a checkpoint
        if game.practice_mode and game.practicemodeobj.is_checkpoint():
            x, y = game.practicemodeobj.get_last_checkpoint()
            self.draw_checkpoint(new_frame, x, y)
        
        # render the new frame
        if not render_raw:
            new_frame.render(self.curr_frame)
        else: 
            new_frame.render_raw()
            
        self.curr_frame = new_frame

    def render_wave_trail(self, frame: CameraFrame, game: "Game") -> None:
        "draws a line between all the wave pivots that are on the screen"
        
        onscreen_pivots = self._get_wave_pivots_in_range(game.player)
        for i in range(1, len(onscreen_pivots)):
            x1, y1 = self.get_screen_coordinates(onscreen_pivots[i-1][0], onscreen_pivots[i-1][1])
            x2, y2 = self.get_screen_coordinates(onscreen_pivots[i][0], onscreen_pivots[i][1])
            
            frame.add_line((x1, y1), (x2, y2), (255, 255, 255))
            
        # draw line from last pivot to player center
        last_pivot = onscreen_pivots[-1]
        player_center = (game.player.pos[0] + game.player.get_hitbox_size()[0]/2, game.player.pos[1] + game.player.get_hitbox_size()[1]/2)
        
        frame.add_line(
            self.get_screen_coordinates(last_pivot[0], last_pivot[1]),
            self.get_screen_coordinates(player_center[0], player_center[1]),
            (255, 255, 255)
        )
    
    def _get_wave_pivots_in_range(self, player: "Player") -> List[Tuple[int, int]]:
        """ Returns all the wave pivots whose x-values are "in range" of the screen. 
        This means all the ones whose x values are in range of camera_left -> camera_right, as
        well as a padding of one extra pivot on either side (so lines can be drawn)
        """

        leftmost_pivot_idx = None
        # binary search for the leftmost pivot that is less than the camera_left
        start, end = 0, len(player.wave_pivot_points) - 1
        while start <= end:
            leftmost_pivot_idx = (start + end) // 2
            if player.wave_pivot_points[leftmost_pivot_idx][0] < self.camera_left:
                start = leftmost_pivot_idx + 1
            else:
                end = leftmost_pivot_idx - 1

        rightmost_pivot_idx = None
        # binary search for the rightmost pivot that is greater than the camera_right
        start, end = 0, len(player.wave_pivot_points) - 1
        while start <= end:
            rightmost_pivot_idx = (start + end) // 2
            if player.wave_pivot_points[rightmost_pivot_idx][0] > (self.camera_left + CameraConstants.screen_width_blocks()):
                end = rightmost_pivot_idx - 1
            else:
                start = rightmost_pivot_idx + 1
                
        if leftmost_pivot_idx is None: leftmost_pivot_idx = 0
        if rightmost_pivot_idx is None: rightmost_pivot_idx = len(player.wave_pivot_points)-1
        
        Logger.log(f"camera left: {self.camera_left}, camera right: {self.camera_left + CameraConstants.screen_width_blocks()}")
        Logger.log(f"xpos of leftmost pivot: {player.wave_pivot_points[leftmost_pivot_idx][0]}, 2nd leftmost: {player.wave_pivot_points[leftmost_pivot_idx+1][0] if len(player.wave_pivot_points) > leftmost_pivot_idx+1 else None}")

        return player.wave_pivot_points[leftmost_pivot_idx:rightmost_pivot_idx+1]
    
    def render_progress_bar(self, frame: CameraFrame, percent: float) -> None:
        """ Adds rectangles that represent the progress bar to the top of the screen """
        
        pbar_outline_left = round((0.5 - CameraConstants.PROGRESS_BAR_WIDTH/2) * frame.width - CameraConstants.PROGRESS_BAR_PADDING_PX)
        pbar_outline_top = CameraConstants.PROGRESS_BAR_MARGIN_TOP_PX - CameraConstants.PROGRESS_BAR_PADDING_PX
        
        # draw a transparent rectangle with a white outline for the border
        frame.add_rect(
            (0, 0, 0, 0),
            pbar_outline_left, pbar_outline_top,
            round(CameraConstants.PROGRESS_BAR_WIDTH * frame.width), CameraConstants.PROGRESS_BAR_HEIGHT_PX+2*CameraConstants.PROGRESS_BAR_PADDING_PX,
            outline_width=1,
            outline_color=(255, 255, 255)
        )
        
        # draw filled rectangle for the progress bar
        pbar_left = pbar_outline_left + CameraConstants.PROGRESS_BAR_PADDING_PX
        pbar_top = pbar_outline_top + CameraConstants.PROGRESS_BAR_PADDING_PX
        
        # use player color 1 for fill color
        frame.add_rect(
            TextureManager.player_color1,
            pbar_left, pbar_top,
            round(percent/100 * CameraConstants.PROGRESS_BAR_WIDTH * frame.width), CameraConstants.PROGRESS_BAR_HEIGHT_PX
        )            
    
    # DEPRECATED - OLD LEVEL EDITOR
    def level_editor_render(self, cursor_pos: tuple, screen_pos: tuple, cur_cursor_obj):

        self.camera_left = screen_pos[0] - CameraConstants.CAMERA_LEFT_OFFSET

        all_strips = []

        cursor_texture = fcode(background="#68FF06")

        cur_y = 0

        for row in self.level[-self.ground:]:
            cur_x = 1

            render_strip_1 = fcode(background=self.level.bg_color) # start as the bg format code
            render_strip_2 = fcode(background=self.level.bg_color) # start as the bg format code
            
            if (floor(self.camera_left)) >= len(row):
                continue # row is all behind us

            partial_render_offset = round(4 * closest_quarter(self.camera_left))
            
            empty_block = " "*(4-partial_render_offset)
            render_strip_1 += empty_block
            render_strip_2 += empty_block
            
            for obj in row[floor(self.camera_left)+1 : min(len(row), floor(self.camera_left + CameraConstants.screen_width_blocks()))]:
                if cursor_pos[1] in {cur_y+1, cur_y-1, cur_y}:
                    if cursor_pos[0] in {cur_x+1, cur_x-1, cur_x}:
                        render_strips = self.draw_cursor((cur_x, cur_y), cursor_pos, cursor_texture, [render_strip_1, render_strip_2], obj, cur_cursor_obj)
                        render_strip_1 = render_strips[0]
                        render_strip_2 = render_strips[1]
                        cur_x += 1
                        continue
                if obj.data is None:
                    empty_block = " "*CameraConstants.BLOCK_WIDTH
                    render_strip_1 += empty_block + fcode(background=self.level.bg_color)
                    render_strip_2 += empty_block + fcode(background=self.level.bg_color)

                else: 
                    render_strip_1 += TextureManager.get_base_texture(obj.data["name"])()[1] + fcode(background=self.level.bg_color)
                    render_strip_2 += TextureManager.get_base_texture(obj.data["name"])()[0] + fcode(background=self.level.bg_color)
                cur_x += 1
            
            render_strip_1 += " "*max(0, GDConstants.term.width-len_no_ansi(render_strip_1))
            render_strip_2 += " "*max(0, GDConstants.term.width-len_no_ansi(render_strip_2))

            all_strips.append(render_strip_2)
            all_strips.append(render_strip_1)
            cur_y += 1

        for i in range(self.ground*CameraConstants.BLOCK_HEIGHT - len(all_strips)):
            print(GDConstants.term.move_yx(i, 0) + fcode(background=self.level.bg_color) + " "*GDConstants.term.width)

        row_in_terminal = (self.ground)*CameraConstants.BLOCK_HEIGHT - len(all_strips)
        for i in range(len(all_strips)):

            print(GDConstants.term.move_yx(row_in_terminal, 0) + all_strips[i])
            row_in_terminal += 1

    def draw_checkpoint(self, frame: CameraFrame, x: float, y: float) -> None:
        """
        Draws a checkpoint at the specified position relative to the given player position.
        Args:
            x (float): The x-coordinate of the checkpoint.
            y (float): The y-coordinate of the checkpoint.
        """

        x_pos, y_pos = self.get_screen_coordinates(x, y)
        y_pos -= EngineConstants.PLAYER_HITBOX_Y * CameraConstants.BLOCK_HEIGHT
        # weird issue where checkpoint is in ground if player is on ground level - move it up if it is
        frame.add_pixels_topleft(x_pos, y_pos, TextureManager.base_textures.get("checkpoint"))
        
    def draw_attempt(self, frame: CameraFrame, player_initial_x: float, attempt: int) -> None:
        """
        Draws the attempt number when the player spawns in.
        Args:
            player_initial_x (float): The initial x-coordinate of the player when the game began.
            attempt (int): The current attempt number to be displayed.
        """
        
        # TODO - this might be optimizable, since we are still constructing the font
        # every frame. Instead, we could just stop doing that once we are fully out of
        # range of the attempt counter.

        x = player_initial_x
        y = 6
        
        pos_on_screen = self.get_screen_coordinates(x, y)
        
        frame.add_text(*pos_on_screen, TextureManager.font_small1, f"Attempt {attempt}")

        # Calculate player's topmost y-coordinate for positioning text
        #player_topmost_y = round((self.ground - y - 1) * CameraConstants.GRID_PX_Y)
        ## offset x coordinate of drawing by where the player is on the screen
        #offset = round(player_x - x + 1)
        #camera_offset_chars = CameraConstants.GRID_PX_X * (CameraConstants.CAMERA_LEFT_OFFSET - offset // 2)
#
        ## Draw the attempt text if it's within the camera's view
        #if camera_offset_chars > 0:
        #    draw_text(f"Attempt: {attempt}", camera_offset_chars, player_topmost_y, bg_color="#007eff")
    
    # DEPRECATED - OLD LEVEL EDITOR
    def draw_cursor(self, cur_pos: tuple, cursor_pos: tuple, cursor_texture, render_strips: list, obj, cur_cursor_obj):
        if obj.data is not None and (obj.data["name"].find("orb") != -1 or obj.data["name"].find("block") != -1):
            render_strips[1] += TextureManager.get_base_texture(obj.data["name"])()[0] + fcode(background=self.level.bg_color)
            render_strips[0] += TextureManager.get_base_texture(obj.data["name"])()[1] + fcode(background=self.level.bg_color)
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
                    render_strips[1] += TextureManager.get_base_texture(cur_cursor_obj.data["name"])()[0] + fcode(background=self.level.bg_color)
                    render_strips[0] += TextureManager.get_base_texture(cur_cursor_obj.data["name"])()[1] + fcode(background=self.level.bg_color)
                else:
                    render_strips = self.draw_center(render_strips, cursor_texture, layer, cur_cursor_obj)
            else:
                render_strips = self.draw_center(render_strips, cursor_texture, layer, obj)
        elif cur_pos[0]-1 == cursor_pos[0]:
            render_strips = self.draw_r_edge(render_strips, cursor_texture, layer, obj)
        elif cur_pos[0]+1 == cursor_pos[0]:
            render_strips = self.draw_l_edge(render_strips, cursor_texture, layer, obj)
        return render_strips

    # DEPRECATED - OLD LEVEL EDITOR
    def draw_center(self, render_strips, cursor_texture, layer, obj):
        empty_block = " "*CameraConstants.BLOCK_WIDTH
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
    
    # DEPRECATED - OLD LEVEL EDITOR
    def draw_l_edge(self, render_strips, cursor_texture, layer, obj):
        empty_block = " "*(CameraConstants.BLOCK_WIDTH//2)
        if obj.data is None:
            if layer[1]:
                render_strips[1] += empty_block + cursor_texture + empty_block
            else:
                render_strips[1] += empty_block + fcode(background=self.level.bg_color) + empty_block
            if layer[0]:
                render_strips[0] += empty_block + cursor_texture + empty_block
            else:
                render_strips[0] += empty_block + fcode(background=self.level.bg_color) + empty_block
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
    
    # DEPRECATED - OLD LEVEL EDITOR
    def draw_r_edge(self, render_strips, cursor_texture,layer, obj):
        empty_block = " "*(CameraConstants.BLOCK_WIDTH//2)
        if obj.data is None:
            if layer[1]:
                render_strips[1] += cursor_texture + empty_block + fcode(background=self.level.bg_color) + empty_block
            else:
                render_strips[1] += empty_block + fcode(background=self.level.bg_color) + empty_block
            if layer[0]:
                render_strips[0] += cursor_texture + empty_block + fcode(background=self.level.bg_color) + empty_block
            else:
                render_strips[0] += empty_block + fcode(background=self.level.bg_color) + empty_block
        else:
            top = TextureManager.get_raw_obj_text(obj.data["name"])[1]
            bottom = TextureManager.get_raw_obj_text(obj.data["name"])[0]
            if layer[1]:
                render_strips[1] += cursor_texture + bottom[len(bottom) - 4:len(bottom) - 2] + fcode(background=self.level.bg_color) + bottom[len(bottom) - 2:]
            else:
                render_strips[1] += bottom
            if layer[0]:
                render_strips[0] += cursor_texture + top[len(top) - 4:len(top) - 2] + fcode(background=self.level.bg_color) + top[len(top) - 2:]
            else:
                render_strips[0] += top
        return render_strips
    