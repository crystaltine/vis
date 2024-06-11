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
from editor.edit_color_popup import EditColorPopup
from editor.edit_color_trigger_popup import EditColorTriggerPopup
from editor.level_settings_popup import LevelSettingsPopup

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

class LevelEditor:
    """ All level-editor related stuff. Instances represent LevelEditors open to specific levels. """
    
    BOTTOM_MENU_HEIGHT = TextureManager.font_small1.font_height + 5 # height of the bottom menu bar in pixels
    BOTTOM_MENU_BG_COLOR = (147, 120, 78, 255)
    BOTTOM_MENU_SAVED_BG_COLOR = (14, 209, 69, 255)
    BUILD_CURSOR_PREVIEW_OPACITY = 0.5 # fraction of 255
    EDIT_CURSOR_FILL_COLOR = (0, 255, 0, 120) 
    EDIT_CURSOR_OUTLINE_COLOR = (180, 255, 150, 220)
    KEYBINDS = {
        "quit": ["q", "\x1b"], # q, esc
        "rotate_clockwise": ["e"],
        "rotate_counterclockwise": ["E"],
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
        "open_settings": ["\x0f"], # ctrl o
        "cycle_object_forward": ["KEY_TAB"], # tab, build mode only
        "cycle_object_backward": ["KEY_BTAB"], # shift tab, build mode only
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
        self.camera_height: int = int(GDConstants.term.height*2-LevelEditor.BOTTOM_MENU_HEIGHT)
        """ The height of the camera in pixels. Camera doesnt take up entire terminal height cuz we have a bottom menu. Will always be even. """
        
        # ensure that camera height is even
        if self.camera_height % 2 == 1:
            self.camera_height -= 1
        
        self.curr_main_frame: CameraFrame = None
        self.curr_bottom_menu_frame: CameraFrame = None
        self.focused_popup: "EditObjectPopup | EditColorPopup | LevelSettingsPopup | None" = None
        """ If true, the editor is currently in a popup window; disable general keybinds & pause main editor rendering. """
        self.rerender_needed = True
        """ If True, the editor will rerender the frame on the next keylistener loop. Set to true when anything on the screen changes. """
        self.showing_save_confirmation = False
        """ Whether or not to render "saved changes!" in the bottom bar instead of build/edit mode. Should be set on save, and unset on the next keypress. """
        self.running = False
        
    def save(self) -> None:
        self.level.metadata["modified_timestamp"] = time.time()
        self.level.write_to_file(self.filepath)
        self.showing_save_confirmation = True
        self.render_bottom_menu()
        
    def undo(self) -> None:
        pass # TODO
    
    def redo(self) -> None:
        pass # TODO
    
    def render_bottom_menu(self) -> None:
        """ Draws the bar at the bottom. It has a 1px border on the top. """
        
        new_frame = CameraFrame(
            size=(self.camera_width, LevelEditor.BOTTOM_MENU_HEIGHT+1), # +1 for the border
            pos=(0, self.camera_height) # +1 for the border
        ) # +1 for the border
        
        # draw a 1px tall rectangle at the top to be the border
        new_frame.add_rect((255, 255, 255, 255), 0, 0, self.camera_width, 1)
        # bg
        color_to_use = LevelEditor.BOTTOM_MENU_SAVED_BG_COLOR if self.showing_save_confirmation else LevelEditor.BOTTOM_MENU_BG_COLOR
        new_frame.add_rect(color_to_use, 0,1, self.camera_width, LevelEditor.BOTTOM_MENU_HEIGHT)
    
        # add left-justified text to the bar at the bottom
        # 2px padding on left
        
        status_text = ...
        if self.showing_save_confirmation:
            status_text = "Saved changes!"
        elif self.mode == 'build':
            status_text = "[Build]"
        elif self.mode == 'edit':
            status_text = "[Edit]"
            
        
        # first, find the center of the bottom menu
        center_y = LevelEditor.BOTTOM_MENU_HEIGHT // 2 + 1 # +1 to account for the border
        new_frame.add_text(2, center_y, TextureManager.font_small1, status_text, 'left')
        
        # if edit mode, add text in bottom right that shows current cursor pos
        cursor_pos_str = f"{self.cursor_position[0]},{self.cursor_position[1]}"
        new_frame.add_text(self.camera_width-2, center_y, TextureManager.font_small1, cursor_pos_str, 'right')
    
        # render the new frame
        if self.curr_bottom_menu_frame is None:
            new_frame.render_raw()
        else:
            new_frame.render(self.curr_bottom_menu_frame)
            
        self.curr_bottom_menu_frame = new_frame
    
    def render_main_editor(self, render_raw: bool = False) -> None:
        """ Draws a single frame of the editor to the screen. Should be overall similar to Camera.render. """
        
        #Logger.log_on_screen(GDConstants.term, f"Rendering frame, cam left,bottom={self.camera_left, self.camera_bottom}, cursor@{self.cursor_position=}")
        
        new_frame = CameraFrame(size=(self.camera_width, self.camera_height))
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
                    
                    #Logger.log(f"[LevelEditor/render_main_editor] Adding texture w shape={obj_texture.shape} @ {xpos_on_screen, ypos_on_screen}")
                    new_frame.add_pixels_centered_at(xpos_on_screen, round(ypos_on_screen), obj_texture)
                    
            curr_screen_y_pos -= CameraConstants.BLOCK_HEIGHT
        
        # draw ground. The top of the ground ground should be at physics y=0.
        # TODO - make ground recolorable/move
        new_frame.add_pixels_topleft(0, round(ground_screen_y_pos), TextureManager.get_curr_ground_texture(self.level, self.camera_left))
        
        # draw cursor
        if self.mode == 'build':
            # draw cursor preview
            cursor_screen_pos = CameraConstants.get_screen_coordinates(self.camera_left, self.camera_bottom, self.camera_height, *self.cursor_position)
            
            # if trigger, dont transform
            #if self.selected_object.type == "color_trigger":
            #    cursor_texture = TextureManager.get_base_texture(self.selected_object)
            #else:
            cursor_texture = TextureManager.set_transparency(TextureManager.get_transformed_texture(self.level, self.selected_object), round(LevelEditor.BUILD_CURSOR_PREVIEW_OPACITY*255))
            #cursor_texture = TextureManager.get_transformed_texture(self.level, self.selected_object)
            
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
        if self.curr_main_frame is None or render_raw:
            new_frame.render_raw()
        else:
            new_frame.render(self.curr_main_frame)
            
        self.curr_main_frame = new_frame
        
    def run_editor(self):
        """ Begins keylistener loops and renders the level editor. this is a BLOCKING call """
        
        self.render_main_editor()
        self.render_bottom_menu()
        self.rerender_needed = False
        
        def key_handler_general(val: "Keystroke") -> None:
            """ General keypress event handler for the editor in any mode """
            self.showing_save_confirmation = False # reset the "saved changes!" message on any keypress
            
            if val in LevelEditor.KEYBINDS["quit"] or val in LevelEditor.KEYBINDS['open_settings']:
                self.focused_popup = LevelSettingsPopup(self.curr_main_frame.copy(), self.level)
                self.focused_popup.render()
                
            elif val in LevelEditor.KEYBINDS['save']:
                self.save()
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
                #Logger.log_on_screen(GDConstants.term, f">>> Toggled leveleditor mode to {self.mode}")
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
                #Logger.log_on_screen(GDConstants.term, f"placing object {self.selected_object} @{self.cursor_position=}")
                self.level.set_object_at(*self.cursor_position, self.selected_object)
                self.rerender_needed = True
            elif val in LevelEditor.KEYBINDS['rotate_clockwise']: # rotate curr object at cursor
                self.selected_object.rotate('clockwise')
                self.rerender_needed = True
            elif val in LevelEditor.KEYBINDS['rotate_counterclockwise']:
                self.selected_object.rotate('counterclockwise')
                self.rerender_needed = True
            elif val in LevelEditor.KEYBINDS['flip_object_horizontal']:
                self.selected_object.reflect('horizontal')
                self.rerender_needed = True
            elif val in LevelEditor.KEYBINDS['flip_object_vertical']:
                self.selected_object.reflect('vertical')
                self.rerender_needed = True
            elif val.name in LevelEditor.KEYBINDS["cycle_object_forward"]:
                curr_obj_type = self.selected_object.data.get("name")
                next_obj_type = OBJECTS.get_next_object_name(curr_obj_type)
                
                num_color_channels = OBJECTS.get_num_color_channels(next_obj_type)
                
                self.selected_object = AbstractLevelObject({
                    "type": next_obj_type,
                    "rotation": CameraConstants.OBJECT_ROTATIONS.UP.value,
                    "reflection": CameraConstants.OBJECT_REFLECTIONS.NONE.value,
                    "color1_channel": 1 if num_color_channels >= 1 else None,
                    "color2_channel": 2 if num_color_channels >= 2 else None
                })
                self.rerender_needed = True
            elif val.name in LevelEditor.KEYBINDS["cycle_object_backward"]:
                curr_obj_type = self.selected_object.data.get("name")
                prev_obj_type = OBJECTS.get_prev_object_name(curr_obj_type)
                
                num_color_channels = OBJECTS.get_num_color_channels(prev_obj_type)
                
                self.selected_object = AbstractLevelObject({
                    "type": prev_obj_type,
                    "rotation": CameraConstants.OBJECT_ROTATIONS.UP.value,
                    "reflection": CameraConstants.OBJECT_REFLECTIONS.NONE.value,
                    "color1_channel": 1 if num_color_channels >= 1 else None,
                    "color2_channel": 2 if num_color_channels >= 2 else None
                })
                self.rerender_needed = True
        
        def key_handler_edit_mode(val: "Keystroke") -> None:
            """ Event handler for keypresses SPECIFIC TO edit mode. """
            
            hovered_obj = self.level.get_object_at(*self.cursor_position)
            if hovered_obj is None: return # no object to edit = edit mode will do nothing.
            
            if val in LevelEditor.KEYBINDS["edit_object"]:
                if hovered_obj.type == "color_trigger":
                    self.focused_popup = EditColorTriggerPopup(self.curr_main_frame.copy(), hovered_obj, self.level)
                    self.focused_popup.render()
                else:
                    self.focused_popup = EditObjectPopup(self.curr_main_frame.copy(), hovered_obj, self.level)
                    self.focused_popup.render()
                    
            elif val in LevelEditor.KEYBINDS['rotate_clockwise']: # rotate curr object at cursor
                hovered_obj.rotate('clockwise')
                self.rerender_needed = True
            elif val in LevelEditor.KEYBINDS['rotate_counterclockwise']:
                hovered_obj.rotate('counterclockwise')
                self.rerender_needed = True
            elif val in LevelEditor.KEYBINDS['flip_object_horizontal']:
                hovered_obj.reflect('horizontal')
                self.rerender_needed = True
            elif val in LevelEditor.KEYBINDS['flip_object_vertical']:
                hovered_obj.reflect('vertical')
                self.rerender_needed = True
        
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
                            returncode = self.focused_popup.handle_key(in_val)
                            match returncode:
                                case "close":
                                    self.focused_popup = None
                                    self.render_main_editor(render_raw=True)
                                    self.render_bottom_menu()
                                case "open-colors": # close popup, open color popup
                                    self.focused_popup = None
                                    self.render_main_editor(render_raw=True)
                                    self.render_bottom_menu()
                                    self.focused_popup = EditColorPopup(self.curr_main_frame.copy(), self.level, "bg")
                                    self.focused_popup.render()
                                case "save-quit": # quit editor
                                    self.save()
                                    self.running = False
                                    break
                            
                        except:
                            Logger.log(f"[LevelEditor/key handler (IN POPUP)]: {traceback.format_exc()}")
                            print(f"[LevelEditor/key handler (IN POPUP)] ERROR: {traceback.format_exc()}")
                            self.running = False
                            
                else: continue                
                
                if self.rerender_needed and self.focused_popup is None: # rerender if stuff changed
                    self.render_main_editor()
                    self.render_bottom_menu()
                    self.rerender_needed = False
