from typing import Literal, TYPE_CHECKING, Callable, Tuple, Any

from logger import Logger
from render.texture_manager import TextureManager
from render.camera_frame import CameraFrame
from level import Level, LevelObject
from render.constants import CameraConstants
from gd_constants import GDConstants
if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

class EditColorPopup:
    """ A popup for editing an RGB color. """
    
    BG_COLOR = (147, 120, 78, 255)
    SELECTED_CHANNEL_BG_COLOR = (123, 102, 70, 255)
    OUTLINE_COLOR = (255, 255, 255, 255)
    FRACTION_OF_SCREEN_WIDTH = 0.5
    FRACTION_OF_SCREEN_HEIGHT = 0.5
    PADDING_Y = 5
    GAP_Y = 4
    PADDING_X = 4
    GAP_X = 4

    def __init__(self, frame: "CameraFrame", on_color_change: Callable[[Tuple[int, int, int]], Any]):
        self.on_color_change = on_color_change
        """ The callback to run if the color is changed. """
        self.last_frame = frame

        self.selected_channel_idx = 0 
        """ 0 for R, 1 for G, 2 for B. represents which color channel the user is currently editing. """
        
        self.right = int(EditColorPopup.FRACTION_OF_SCREEN_WIDTH * frame.width)
        self.left = frame.width - self.right
        self.horiz_center = (self.left + self.right) // 2
        self.bottom = int(EditColorPopup.FRACTION_OF_SCREEN_HEIGHT * frame.height)
        self.top = frame.height - self.bottom
        self.vert_center = (self.top + self.bottom) // 2
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        
    def render(self):
        """ Draws this popup to the center of the frame provided, and renders the frame. """

        # add box and title
        new_frame = self.last_frame.copy()
        new_frame.add_rect(
            EditColorPopup.BG_COLOR,
            self.left, self.top, self.width, self.height,
            outline_color=EditColorPopup.OUTLINE_COLOR,
            outline_width=2,
            anchor="top-left"
        )
        new_frame.add_text(self.horiz_center, self.top + EditColorPopup.PADDING_Y, TextureManager.font_small1, "Edit Color")
        
        # add setting rows (TODO - detect number of color object supports - only render that many)
        curr_y_pos = self.top + EditColorPopup.PADDING_Y + TextureManager.font_small1.font_height + EditColorPopup.GAP_Y
        
        BUTTON_STARTING_X_POS = self.right - EditColorPopup.PADDING_X - int(3.5*EditColorPopup.BUTTON_SIZE) - 3*EditColorPopup.GAP_X

        ####### Color 1
        curr_x_pos = BUTTON_STARTING_X_POS
        if self.selected_setting_idx == 0: # draw shaded rect if selected
            new_frame.add_rect(
                EditColorPopup.SELECTED_CHANNEL_BG_COLOR,
                self.left, curr_y_pos-EditColorPopup.GAP_Y//2-EditColorPopup.BUTTON_SIZE//2//2,
                self.width, TextureManager.font_small1.font_height+EditColorPopup.GAP_Y
            )
        new_frame.add_text(self.left + EditColorPopup.PADDING_X, curr_y_pos, TextureManager.font_small1, "Color 1", anchor='left')
        # draw color preview
        new_frame.add_rect(
            self.level.get_colors_of(self.obj)[0],
            curr_x_pos, curr_y_pos,
            EditColorPopup.BUTTON_SIZE, EditColorPopup.BUTTON_SIZE,
            anchor="center"
        )
        curr_x_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_X

        # draw minus button
        button = getattr(EditColorPopup, f"minus_button{'_pressed' if self.selected_button_idx == 0 and self.selected_setting_idx == 0 else ''}")
        new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
        curr_x_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_X

        # draw color number
        new_frame.add_text(curr_x_pos, curr_y_pos, TextureManager.font_small1, str(self.obj.color1_channel))
        curr_x_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_X

        # draw plus button
        button = getattr(EditColorPopup, f"plus_button{'_pressed' if self.selected_button_idx == 1 and self.selected_setting_idx == 0 else ''}")
        new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)

        curr_y_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_Y
        


        ####### Color 2
        curr_x_pos = BUTTON_STARTING_X_POS
        if self.selected_setting_idx == 1: # draw shaded rect if selected
            new_frame.add_rect(
                EditColorPopup.SELECTED_CHANNEL_BG_COLOR,
                self.left, curr_y_pos-EditColorPopup.GAP_Y//2-EditColorPopup.BUTTON_SIZE//2//2,
                self.width, TextureManager.font_small1.font_height+EditColorPopup.GAP_Y
            )
        new_frame.add_text(self.left + EditColorPopup.PADDING_X, curr_y_pos, TextureManager.font_small1, "Color 2", anchor='left')
        # draw color preview
        new_frame.add_rect(
            self.level.get_colors_of(self.obj)[1],
            curr_x_pos, curr_y_pos,
            EditColorPopup.BUTTON_SIZE, EditColorPopup.BUTTON_SIZE,
            anchor="center"
        )
        curr_x_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_X

        # draw minus button
        button = getattr(EditColorPopup, f"minus_button{'_pressed' if self.selected_button_idx == 0 and self.selected_setting_idx == 1 else ''}")
        new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
        curr_x_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_X

        # draw color number
        new_frame.add_text(curr_x_pos, curr_y_pos, TextureManager.font_small1, str(self.obj.color2_channel))
        curr_x_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_X
        
        # draw plus button
        button = getattr(EditColorPopup, f"plus_button{'_pressed' if self.selected_button_idx == 1 and self.selected_setting_idx == 1 else ''}")
        new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)

        curr_y_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_Y
        


        ####### Rotations (buttons are 9px)
        curr_x_pos = BUTTON_STARTING_X_POS
        if self.selected_setting_idx == 2: # draw shaded rect if selected
            new_frame.add_rect(
                EditColorPopup.SELECTED_CHANNEL_BG_COLOR,
                self.left, curr_y_pos-EditColorPopup.GAP_Y//2-EditColorPopup.BUTTON_SIZE//2,
                self.width, EditColorPopup.BUTTON_SIZE+EditColorPopup.GAP_Y
            )
        for rotation in CameraConstants.OBJECT_ROTATIONS:
            button = getattr(EditColorPopup, f"rotation_{rotation.value}_button_{'pressed' if self.obj.rotation == rotation.value else 'unpressed'}")
            new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
            curr_x_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_X
        curr_y_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_Y
        


        ####### Reflections (buttons are also 9px)
        curr_x_pos = BUTTON_STARTING_X_POS
        if self.selected_setting_idx == 3: # draw shaded rect if selected
            new_frame.add_rect(
                EditColorPopup.SELECTED_CHANNEL_BG_COLOR,
                self.left, curr_y_pos-EditColorPopup.GAP_Y//2-EditColorPopup.BUTTON_SIZE//2,
                self.width, EditColorPopup.BUTTON_SIZE+EditColorPopup.GAP_Y
            )
        for reflection in CameraConstants.OBJECT_REFLECTIONS:
            button = getattr(EditColorPopup, f"reflection_{reflection.value}_button_{'pressed' if self.obj.reflection == reflection.value else 'unpressed'}")
            new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
            curr_x_pos += EditColorPopup.BUTTON_SIZE + EditColorPopup.GAP_X



        new_frame.render(self.last_frame)
        self.last_frame = new_frame

    def handle_key(self, key: "Keystroke") -> bool:
        """ Performs actions on this instance based on key pressed. Returns True if popup closed, False otherwise. """
        if key == "\x1b":
            return True
        elif key.name in ["KEY_TAB", "KEY_DOWN"]: # go down (forward) one row
            self.selected_channel_idx = (self.selected_channel_idx + 1) % 3
        elif key.name in ["KEY_BTAB", "KEY_UP"]: # shift+tab; key code is \x1b[Z, go up (back) one row
            self.selected_channel_idx = (self.selected_channel_idx - 1) % 3

        # L/R arrow keys - change the currently selected button
        elif key.name == "KEY_RIGHT":
            self.selected_button_idx = (self.selected_button_idx + 1) % (self.available_settings[self.selected_setting_idx][1])
            self.edit_object_rotation_reflection(self.selected_button_idx)
        elif key.name == "KEY_LEFT":
            self.selected_button_idx = (self.selected_button_idx - 1) % (self.available_settings[self.selected_setting_idx][1])
            self.edit_object_rotation_reflection(self.selected_button_idx)
        elif key.name == "KEY_ENTER": # only for color settings
            delta = self.selected_button_idx*2 - 1 # maps 0,1 -> -1, 1 (for adding or subtracting)
            
            if self.selected_setting_idx == 0: # color channel 1
                self.obj.color1_channel += delta
                self.obj.color1_channel = max(self.obj.color1_channel, 0)
            elif self.selected_setting_idx == 1: # color channel 1
                self.obj.color2_channel += delta
                self.obj.color2_channel = max(self.obj.color2_channel, 0)

        self.render()
        return False
    