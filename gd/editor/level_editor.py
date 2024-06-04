from typing import Tuple, Literal, TYPE_CHECKING
from math import floor, ceil
import time
import traceback

from logger import Logger
from render.constants import CameraConstants
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from gd_constants import GDConstants
from engine.objects import OBJECTS
from level import Level, LevelObject, AbstractLevelObject
from editor.edit_object_popup import EditObjectPopup
from editor.level_settings_popup import LevelSettingsPopup

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

class LevelEditor:
    """ All level-editor related stuff. Instances represent LevelEditors open to specific levels. """
    
    BOTTOM_MENU_HEIGHT = 0.25 # fraction of screen height
    BUILD_CURSOR_PREVIEW_OPACITY = 0.5 # fraction of 255
    EDIT_CURSOR_FILL_COLOR = (0, 255, 0, 120) 
    EDIT_CURSOR_OUTLINE_COLOR = (180, 255, 150, 220)
    KEYBINDS = {
        "quit": ["q", "\x1b"], # q, esc
        "rotate_object_clockwise": ["r"],
        "rotate_object_counterclockwise": ["R"],
        "flip_object_horizontal": ["h"],
        "flip_object_vertical": ["v"],
        "delete_object": ["\x7f", "\x1b[3~"], # del, backspace
        "copy": ["\x03"], # ctrl c
        "paste": ["\x16"], # ctrl v
        "save": ["\x13"], # ctrl s
        "undo": ["\x1a"], # ctrl z
        "redo": ["\x19"], # ctrl y
        "move_camera_up": ["KEY_UP"],
        "move_camera_down": ["KEY_DOWN"],
        "move_camera_left": ["KEY_LEFT"],
        "move_camera_right": ["KEY_RIGHT"],
        "move_cursor_up": ["w"],
        "move_cursor_down": ["s"],
        "move_cursor_left": ["a"],
        "move_cursor_right": ["d"],
        "toggle_mode": ["\x05"], # ctrl e
        "place_object": ["\r", " "], # (enter, space), build mode only
        "edit_object": ["\r"], # (enter), edit mode only
    }
    
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.level = Level.parse_from_file(filepath)
        
        self.mode: Literal['build', 'edit'] = 'build'
        """ 
        build mode or edit mode.
        
        In build: Cursor can have an object, and renders a half-opacity preview of the object being placed.
        Can place, delete, rotate, and reflect objects.
        
        In edit: Cursor is just a pointer. Renders as a green box over the currently selected grid position.
        Can edit object color channels, and select a range.
        """
        
        self.clipboard: AbstractLevelObject | None = None
        """ Abstract object that is copied to the clipboard. """
        self.undo_stack = []
        self.redo_stack = []
        
        self.cursor_position: Tuple[int, int] = (0, 0)
        """ Position of the CURSOR. This is independent of the screen position. """        
        self.selected_object: AbstractLevelObject = AbstractLevelObject({
            "type": "block0_0",
            "rotation": CameraConstants.OBJECT_ROTATIONS.UP.value,
            "reflection": CameraConstants.OBJECT_REFLECTIONS.NONE.value,
            "color1_channel": 1,
            "color2_channel": 2,
        }) # TODO - this is a really annoying way of creating lvlobjects. Maybe implement a default function?
        """ Object dict of the currently selected object. Can be None. """
        
        self.camera_left: int = 0
        """ The x-position of the left edge of the camera. """
        self.camera_bottom: int = -CameraConstants.GROUND_HEIGHT
        """ The y-position of the bottom edge of the camera. """
        self.camera_width: int = GDConstants.term.width
        """ The width of the camera in pixels. For now, its just the terminal width. """
        self.camera_height: int = int(GDConstants.term.height*2*(1-LevelEditor.BOTTOM_MENU_HEIGHT))
        """ The height of the camera in pixels. Camera doesnt take up entire terminal height cuz we have a bottom menu. Will always be even. """
        
        # ensure that camera height is even
        if self.camera_height % 2 == 1:
            self.camera_height -= 1
        
        self.curr_frame: CameraFrame = None
        self.focused_popup: "EditObjectPopup | LevelSettingsPopup | None" = None
        """ If true, the editor is currently in a popup window; disable general keybinds & pause main editor rendering. """
        self.rerender_needed = True
        """ If True, the editor will rerender the frame on the next keylistener loop. Set to true when anything on the screen changes. """
        self.running = False
        
    def save(self) -> None:
        self.level.metadata["modified_timestamp"] = time.time()
        self.level.write_to_file(self.filepath)
        
    def undo(self) -> None:
        pass # TODO
    
    def redo(self) -> None:
        pass # TODO
    
    def render_main_editor(self) -> None:
        """ Draws a single frame of the editor to the screen. Should be overall similar to Camera.render. """
        
        #Logger.log_on_screen(GDConstants.term, f"Rendering frame, cam left,bottom={self.camera_left, self.camera_bottom}, cursor@{self.cursor_position=}")
        
        new_frame = CameraFrame(GDConstants.term, size=(self.camera_width, self.camera_height))
        new_frame.fill(self.level.bg_color)
        #new_frame.fill([randint(0, 255) for _ in range(3)])

        camera_right = self.camera_left + self.camera_width / CameraConstants.BLOCK_WIDTH
        camera_top = self.camera_bottom + self.camera_height / CameraConstants.BLOCK_HEIGHT

        visible_vert_range = max(0, floor(self.camera_bottom)), min(self.level.height, 1+ceil(self.camera_bottom + new_frame.height / CameraConstants.BLOCK_HEIGHT))
        # this should be smth like (5, 12) which is the range of y-pos of the grid that is visible on the screen. Exclusive of the second number (thats why we +1)

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
                    obj_texture = TextureManager.get_transformed_texture(self.level, obj)
                    
                    new_frame.add_pixels_centered_at(xpos_on_screen, round(ypos_on_screen), obj_texture)
                    
            curr_screen_y_pos -= CameraConstants.BLOCK_HEIGHT
        
        # draw ground. The top of the ground ground should be at physics y=0.
        # TODO - make ground recolorable/move
        new_frame.add_pixels_topleft(0, round(ground_screen_y_pos), TextureManager.base_textures.get("ground"))
        
        # draw cursor
        if self.mode == 'build':
            # draw cursor preview
            cursor_screen_pos = CameraConstants.get_screen_coordinates(self.camera_left, self.camera_bottom, self.camera_height, *self.cursor_position)
            cursor_texture = TextureManager.set_transparency(TextureManager.get_transformed_texture(self.level, self.selected_object), round(LevelEditor.BUILD_CURSOR_PREVIEW_OPACITY*255))
            
            # convert top left to center
            cursor_screen_pos = (cursor_screen_pos[0] + CameraConstants.BLOCK_WIDTH // 2, cursor_screen_pos[1] + CameraConstants.BLOCK_HEIGHT // 2)
            
            new_frame.add_pixels_centered_at(*cursor_screen_pos, cursor_texture)
        elif self.mode == 'edit':
            # draw a green box around the cursor position. Also 1px outline.
            cursor_screen_pos = CameraConstants.get_screen_coordinates(self.camera_left, self.camera_bottom, self.camera_height, *self.cursor_position)
            new_frame.add_rect(
                LevelEditor.EDIT_CURSOR_FILL_COLOR, 
                cursor_screen_pos[0], cursor_screen_pos[1], 
                CameraConstants.BLOCK_WIDTH, CameraConstants.BLOCK_HEIGHT,
                outline_color=LevelEditor.EDIT_CURSOR_OUTLINE_COLOR, outline_width=1
            )
            
        
        # render the new frame
        if self.curr_frame is not None:
            new_frame.render(self.curr_frame)
        else:
            new_frame.render_raw()
            
        self.curr_frame = new_frame
        
    def run_editor(self):
        """ Begins keylistener loops and renders the level editor. """
        
        self.render_main_editor()
        self.rerender_needed = False
        
        def key_handler_general(val: "Keystroke") -> None:
            """ General keypress event handler for the editor in any mode """
            if val in LevelEditor.KEYBINDS["quit"]:
                self.running = False
            elif val in LevelEditor.KEYBINDS['save']:
                self.save()
            elif val in LevelEditor.KEYBINDS['rotate_object_clockwise']:
                pass # TODO
            elif val in LevelEditor.KEYBINDS['rotate_object_counterclockwise']:
                pass # TODO
            elif val in LevelEditor.KEYBINDS['flip_object_horizontal']:
                pass # TODO
            elif val in LevelEditor.KEYBINDS['flip_object_vertical']:
                pass # TODO
            elif val in LevelEditor.KEYBINDS['delete_object']:
                self.level.set_object_at(*self.cursor_position, None)    
                self.rerender_needed = True 
            elif val in LevelEditor.KEYBINDS['copy']:
                self.clipboard = self.level.get_object_at(*self.cursor_position).abstract_copy() 
            elif val in LevelEditor.KEYBINDS['paste']:
                self.level.set_object_at(*self.cursor_position, self.clipboard)
                self.rerender_needed = True 
            elif val in LevelEditor.KEYBINDS['undo']:
                self.undo()
                self.rerender_needed = True 
            elif val in LevelEditor.KEYBINDS['redo']:
                self.redo()
                self.rerender_needed = True 
                
            elif val in LevelEditor.KEYBINDS['toggle_mode']:
                self.mode = 'build' if self.mode == 'edit' else 'edit'
                Logger.log_on_screen(GDConstants.term, f">>> Toggled leveleditor mode to {self.mode}")
                self.rerender_needed = True
            
            # moving - i know this type of definition is inefficient, but it allows for custom keybinding
            elif val in LevelEditor.KEYBINDS['move_cursor_up']:
                self.cursor_position = (self.cursor_position[0], self.cursor_position[1]+1)
                if self.cursor_position[1] >= floor(self.camera_bottom + self.camera_height / CameraConstants.BLOCK_HEIGHT):
                    self.camera_bottom += 1
                self.rerender_needed = True 
            elif val in LevelEditor.KEYBINDS['move_cursor_right']:
                self.cursor_position = (self.cursor_position[0]+1, self.cursor_position[1])
                if self.cursor_position[0] >= floor(self.camera_left + self.camera_width / CameraConstants.BLOCK_WIDTH):
                    self.camera_left += 1
                self.rerender_needed = True 
            elif val in LevelEditor.KEYBINDS['move_cursor_down']:
                self.cursor_position = (self.cursor_position[0], max(0, self.cursor_position[1]-1))
                if self.cursor_position[1] < self.camera_bottom:
                    self.camera_bottom -= 1
                self.rerender_needed = True 
            elif val in LevelEditor.KEYBINDS['move_cursor_left']:
                self.cursor_position = (max(0, self.cursor_position[0]-1), self.cursor_position[1])
                if self.cursor_position[0] < self.camera_left:
                    self.camera_left -= 1
                self.rerender_needed = True 
            
            elif val.name in LevelEditor.KEYBINDS['move_camera_up']:
                self.camera_bottom += 1
                self.rerender_needed = True 
            elif val.name in LevelEditor.KEYBINDS['move_camera_right']:
                self.camera_left += 1
                self.rerender_needed = True 
            elif val.name in LevelEditor.KEYBINDS['move_camera_down']:
                self.camera_bottom -= 1
                self.camera_bottom = max(-CameraConstants.GROUND_HEIGHT, self.camera_bottom)
                self.rerender_needed = True 
            elif val.name in LevelEditor.KEYBINDS['move_camera_left']:
                self.camera_left -= 1
                self.camera_left = max(0, self.camera_left)
                self.rerender_needed = True 
            
        def key_handler_build_mode(val: "Keystroke") -> None:
            """ Event handler for keypresses SPECIFIC TO build mode. """
            if val in LevelEditor.KEYBINDS["place_object"]:
                Logger.log_on_screen(GDConstants.term, f"placing object {self.selected_object} @{self.cursor_position=}")
                self.level.set_object_at(*self.cursor_position, self.selected_object)
                self.rerender_needed = True
        
        def key_handler_edit_mode(val: "Keystroke") -> None:
            """ Event handler for keypresses SPECIFIC TO edit mode. """
            if val in LevelEditor.KEYBINDS["edit_object"]:
                hovered_obj = self.level.get_object_at(*self.cursor_position)
                if hovered_obj is not None:
                    self.focused_popup = EditObjectPopup(self.curr_frame, hovered_obj)
                    self.focused_popup.render()
        
        self.running = True
        while self.running:
            with GDConstants.term.cbreak():
                in_val = GDConstants.term.inkey(0.01)
                
                if in_val:
                    if self.focused_popup is None:
                        try:
                            key_handler_general(in_val)
                            key_handler_build_mode(in_val) if self.mode == 'build' else key_handler_edit_mode(in_val)
                        except:
                            Logger.log(f"[LevelEditor/key handler (not in popup)]: {traceback.format_exc()}")
                            print(f"[LevelEditor/key handler (not in popup)] ERROR: {traceback.format_exc()}")
                            self.running = False
                    else:
                        try:
                            should_quit = self.focused_popup.handle_key(in_val)
                            if should_quit:
                                self.focused_popup = None
                                self.rerender_needed = True
                        except:
                            Logger.log(f"[LevelEditor/key handler (IN POPUP)]: {traceback.format_exc()}")
                            print(f"[LevelEditor/key handler (IN POPUP)] ERROR: {traceback.format_exc()}")
                            self.running = False
                else: continue
                
                if self.rerender_needed and self.focused_popup is None: # rerender if stuff changed
                    self.render_main_editor()
                    self.rerender_needed = False
