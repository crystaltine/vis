from typing import Literal, TYPE_CHECKING

from logger import Logger
from render.texture_manager import TextureManager
from render.camera_frame import CameraFrame
from level import Level, LevelObject
from render.constants import CameraConstants

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

class EditObjectPopup:
    """ stuff for rendering the edit object popup (allows editing of color channels, rotation, and reflection) (maybe more later? idk) """
    
    BG_COLOR = (147, 120, 78, 255)
    OUTLINE_COLOR = (255, 255, 255, 255)
    FRACTION_OF_SCREEN_WIDTH = 0.8
    FRACTION_OF_SCREEN_HEIGHT = 0.9
    PADDING_Y = 5
    GAP_Y = 4
    PADDING_X = 4
    GAP_X = 4
    SMALL_BUTTON_SIDELEN = 9
    
    # preload textures
    rotation_up_button_unpressed = TextureManager.compile_texture("./assets/level_editor/rotation_buttons/rotation_button_up_unpressed.png")
    rotation_up_button_pressed = TextureManager.compile_texture("./assets/level_editor/rotation_buttons/rotation_button_up_pressed.png")
    rotation_right_button_unpressed = TextureManager.compile_texture("./assets/level_editor/rotation_buttons/rotation_button_right_unpressed.png")
    rotation_right_button_pressed = TextureManager.compile_texture("./assets/level_editor/rotation_buttons/rotation_button_right_pressed.png")
    rotation_down_button_unpressed = TextureManager.compile_texture("./assets/level_editor/rotation_buttons/rotation_button_down_unpressed.png")
    rotation_down_button_pressed = TextureManager.compile_texture("./assets/level_editor/rotation_buttons/rotation_button_down_pressed.png")
    rotation_left_button_unpressed = TextureManager.compile_texture("./assets/level_editor/rotation_buttons/rotation_button_left_unpressed.png")
    rotation_left_button_pressed = TextureManager.compile_texture("./assets/level_editor/rotation_buttons/rotation_button_left_pressed.png")
    
    reflection_none_button_unpressed = TextureManager.compile_texture("./assets/level_editor/reflection_buttons/reflection_none_button_unpressed.png")
    reflection_none_button_pressed = TextureManager.compile_texture("./assets/level_editor/reflection_buttons/reflection_none_button_pressed.png")
    reflection_horizontal_button_unpressed = TextureManager.compile_texture("./assets/level_editor/reflection_buttons/reflection_horizontal_button_unpressed.png")
    reflection_horizontal_button_pressed = TextureManager.compile_texture("./assets/level_editor/reflection_buttons/reflection_horizontal_button_pressed.png")
    reflection_vertical_button_unpressed = TextureManager.compile_texture("./assets/level_editor/reflection_buttons/reflection_vertical_button_unpressed.png")
    reflection_vertical_button_pressed = TextureManager.compile_texture("./assets/level_editor/reflection_buttons/reflection_vertical_button_pressed.png")
    reflection_both_button_unpressed = TextureManager.compile_texture("./assets/level_editor/reflection_buttons/reflection_both_button_unpressed.png")
    reflection_both_button_pressed = TextureManager.compile_texture("./assets/level_editor/reflection_buttons/reflection_both_button_pressed.png")
    
    def __init__(self, frame: CameraFrame, obj: LevelObject):
        self.obj = obj
        self.last_frame = frame
        
        self.available_settings = ['color1', 'color2', 'rotation', 'reflection']
        self.selected_setting_idx = 0
        self.selected_button_idx = 0
        
        self.right = int(EditObjectPopup.FRACTION_OF_SCREEN_WIDTH * frame.width)
        self.left = frame.width - self.right
        self.horiz_center = (self.left + self.right) // 2
        self.bottom = int(EditObjectPopup.FRACTION_OF_SCREEN_HEIGHT * frame.height)
        self.top = frame.height - self.bottom
        self.vert_center = (self.top + self.bottom) // 2
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        
    def render(self):
        """ Draws this popup to the center of the frame provided, and renders the frame. """

        # add box and title
        new_frame = self.last_frame.copy()
        new_frame.add_rect(
            EditObjectPopup.BG_COLOR,
            self.left, self.top, self.width, self.height,
            outline_color=EditObjectPopup.OUTLINE_COLOR,
            outline_width=2,
            anchor="top-left"
        )
        new_frame.add_text(self.horiz_center, self.top + EditObjectPopup.PADDING_Y, TextureManager.font_small1, "Edit Object")
        
        # add setting rows (TODO - detect number of color object supports - only render that many)
        # (for now, just renders two)
        curr_y_pos = self.top + EditObjectPopup.PADDING_Y + TextureManager.font_small1.font_height + EditObjectPopup.GAP_Y
        
        new_frame.add_text(self.left + EditObjectPopup.PADDING_X, curr_y_pos, TextureManager.font_small1, "Color 1", anchor='left')
        # add setting (TODO)
        curr_y_pos += TextureManager.font_small1.font_height + EditObjectPopup.GAP_Y
        
        new_frame.add_text(self.left + EditObjectPopup.PADDING_X, curr_y_pos, TextureManager.font_small1, "Color 2", anchor='left')
        # add setting (TODO)
        curr_y_pos += TextureManager.font_small1.font_height + EditObjectPopup.GAP_Y
        
        #new_frame.add_text(self.left + EditObjectPopup.PADDING_X, curr_y_pos, TextureManager.font_small1, "Rotation", anchor='left')
        # Rotations (buttons are 9px)
        curr_x_pos = self.right - EditObjectPopup.PADDING_X - int(3.5*EditObjectPopup.SMALL_BUTTON_SIDELEN) - 3*EditObjectPopup.GAP_X
        for rotation in CameraConstants.OBJECT_ROTATIONS:
            button = getattr(EditObjectPopup, f"rotation_{rotation.value}_button_{'pressed' if self.obj.rotation == rotation.value else 'unpressed'}")
            new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
            curr_x_pos += EditObjectPopup.SMALL_BUTTON_SIDELEN + EditObjectPopup.GAP_X
        curr_y_pos += EditObjectPopup.SMALL_BUTTON_SIDELEN + EditObjectPopup.GAP_Y
        
        #new_frame.add_text(self.left + EditObjectPopup.PADDING_X, curr_y_pos, TextureManager.font_small1, "Reflection", anchor='left')
        # Reflections (buttons are also 9px)
        curr_x_pos = self.right - EditObjectPopup.PADDING_X - int(3.5*EditObjectPopup.SMALL_BUTTON_SIDELEN) - 3*EditObjectPopup.GAP_X
        for reflection in CameraConstants.OBJECT_REFLECTIONS:
            button = getattr(EditObjectPopup, f"reflection_{reflection.value}_button_{'pressed' if self.obj.reflection == reflection.value else 'unpressed'}")
            new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
            curr_x_pos += EditObjectPopup.SMALL_BUTTON_SIDELEN + EditObjectPopup.GAP_X
        
        new_frame.render(self.last_frame)
        self.last_frame = new_frame
    
    def handle_key(self, key: "Keystroke") -> bool:
        """ Performs actions on this instance based on key pressed. Returns True if popup closed, False otherwise. """
        if key == "\x1b":
            return True
    