from typing import Literal, TYPE_CHECKING

from logger import Logger
from render.texture_manager import TextureManager
from render.camera_frame import CameraFrame
from level import Level, LevelObject
from render.constants import CameraConstants
from gd_constants import GDConstants

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

class EditObjectPopup:
    """ stuff for rendering the edit object popup (allows editing of color channels, rotation, and reflection) (maybe more later? idk) """
    
    BG_COLOR = (147, 120, 78, 255)
    SELECTED_SETTING_BG_COLOR = (123, 102, 70, 255)
    OUTLINE_COLOR = (255, 255, 255, 255)
    FRACTION_OF_SCREEN_WIDTH = 0.8
    FRACTION_OF_SCREEN_HEIGHT = 0.9
    PADDING_Y = 5
    GAP_Y = 4
    PADDING_X = 4
    GAP_X = 4
    BUTTON_SIZE = 9
    
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
    
    plus_button = TextureManager.compile_texture("./assets/level_editor/value_buttons/plus_button.png")
    plus_button_pressed = TextureManager.compile_texture("./assets/level_editor/value_buttons/plus_button_pressed.png")
    minus_button = TextureManager.compile_texture("./assets/level_editor/value_buttons/minus_button.png")
    minus_button_pressed = TextureManager.compile_texture("./assets/level_editor/value_buttons/minus_button_pressed.png")

    def __init__(self, frame: CameraFrame, obj: LevelObject, level: Level):
        self.obj = obj
        self.level = level
        self.last_frame = frame
        
        self.available_settings = [
            ('color1', 2),
            ('color2', 2), 
            ('rotation', 4), 
            ('reflection', 4)
        ]
        """ List of tuples of (setting name, number of selectable buttons it has) """

        self.selected_setting_idx = 0
        self.selected_button_idx = 0
        """ SHOULD ONLY BE USED FOR COLOR CHANNEL SETTINGS """
        
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
        curr_y_pos = self.top + EditObjectPopup.PADDING_Y + TextureManager.font_small1.font_height + EditObjectPopup.GAP_Y
        
        BUTTON_STARTING_X_POS = self.right - EditObjectPopup.PADDING_X - int(3.5*EditObjectPopup.BUTTON_SIZE) - 3*EditObjectPopup.GAP_X

        ####### Color 1
        curr_x_pos = BUTTON_STARTING_X_POS
        if self.selected_setting_idx == 0: # draw shaded rect if selected
            new_frame.add_rect(
                EditObjectPopup.SELECTED_SETTING_BG_COLOR,
                self.left, curr_y_pos-EditObjectPopup.GAP_Y//2-EditObjectPopup.BUTTON_SIZE//2//2,
                self.width, TextureManager.font_small1.font_height+EditObjectPopup.GAP_Y
            )
        new_frame.add_text(self.left + EditObjectPopup.PADDING_X, curr_y_pos, TextureManager.font_small1, "Color 1", anchor='left')
        # draw color preview
        new_frame.add_rect(
            self.level.get_colors_of(self.obj)[0],
            curr_x_pos, curr_y_pos,
            EditObjectPopup.BUTTON_SIZE, EditObjectPopup.BUTTON_SIZE,
            anchor="center"
        )
        curr_x_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_X

        # draw minus button
        button = getattr(EditObjectPopup, f"minus_button{'_pressed' if self.selected_button_idx == 0 and self.selected_setting_idx == 0 else ''}")
        new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
        curr_x_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_X

        # draw color number
        new_frame.add_text(curr_x_pos, curr_y_pos, TextureManager.font_small1, str(self.obj.color1_channel))
        curr_x_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_X

        # draw plus button
        button = getattr(EditObjectPopup, f"plus_button{'_pressed' if self.selected_button_idx == 1 and self.selected_setting_idx == 0 else ''}")
        new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)

        curr_y_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_Y
        


        ####### Color 2
        curr_x_pos = BUTTON_STARTING_X_POS
        if self.selected_setting_idx == 1: # draw shaded rect if selected
            new_frame.add_rect(
                EditObjectPopup.SELECTED_SETTING_BG_COLOR,
                self.left, curr_y_pos-EditObjectPopup.GAP_Y//2-EditObjectPopup.BUTTON_SIZE//2//2,
                self.width, TextureManager.font_small1.font_height+EditObjectPopup.GAP_Y
            )
        new_frame.add_text(self.left + EditObjectPopup.PADDING_X, curr_y_pos, TextureManager.font_small1, "Color 2", anchor='left')
        # draw color preview
        new_frame.add_rect(
            self.level.get_colors_of(self.obj)[1],
            curr_x_pos, curr_y_pos,
            EditObjectPopup.BUTTON_SIZE, EditObjectPopup.BUTTON_SIZE,
            anchor="center"
        )
        curr_x_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_X

        # draw minus button
        button = getattr(EditObjectPopup, f"minus_button{'_pressed' if self.selected_button_idx == 0 and self.selected_setting_idx == 1 else ''}")
        new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
        curr_x_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_X

        # draw color number
        new_frame.add_text(curr_x_pos, curr_y_pos, TextureManager.font_small1, str(self.obj.color2_channel))
        curr_x_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_X
        
        # draw plus button
        button = getattr(EditObjectPopup, f"plus_button{'_pressed' if self.selected_button_idx == 1 and self.selected_setting_idx == 1 else ''}")
        new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)

        curr_y_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_Y
        


        ####### Rotations (buttons are 9px)
        curr_x_pos = BUTTON_STARTING_X_POS
        if self.selected_setting_idx == 2: # draw shaded rect if selected
            new_frame.add_rect(
                EditObjectPopup.SELECTED_SETTING_BG_COLOR,
                self.left, curr_y_pos-EditObjectPopup.GAP_Y//2-EditObjectPopup.BUTTON_SIZE//2,
                self.width, EditObjectPopup.BUTTON_SIZE+EditObjectPopup.GAP_Y
            )
        for rotation in CameraConstants.OBJECT_ROTATIONS:
            button = getattr(EditObjectPopup, f"rotation_{rotation.value}_button_{'pressed' if self.obj.rotation == rotation.value else 'unpressed'}")
            new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
            curr_x_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_X
        curr_y_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_Y
        


        ####### Reflections (buttons are also 9px)
        curr_x_pos = BUTTON_STARTING_X_POS
        if self.selected_setting_idx == 3: # draw shaded rect if selected
            new_frame.add_rect(
                EditObjectPopup.SELECTED_SETTING_BG_COLOR,
                self.left, curr_y_pos-EditObjectPopup.GAP_Y//2-EditObjectPopup.BUTTON_SIZE//2,
                self.width, EditObjectPopup.BUTTON_SIZE+EditObjectPopup.GAP_Y
            )
        for reflection in CameraConstants.OBJECT_REFLECTIONS:
            button = getattr(EditObjectPopup, f"reflection_{reflection.value}_button_{'pressed' if self.obj.reflection == reflection.value else 'unpressed'}")
            new_frame.add_pixels_centered_at(curr_x_pos, curr_y_pos, button)
            curr_x_pos += EditObjectPopup.BUTTON_SIZE + EditObjectPopup.GAP_X



        new_frame.render(self.last_frame)
        self.last_frame = new_frame

    def edit_object_rotation_reflection(self, new_idx: int) -> int:
        if self.selected_setting_idx == 2: # ROTATIONS
            self.obj.rotation = list(CameraConstants.OBJECT_ROTATIONS)[new_idx].value
        if self.selected_setting_idx == 3: # REFLECTIONS
            self.obj.reflection = list(CameraConstants.OBJECT_REFLECTIONS)[new_idx].value
    
    def get_selected_button_index(self) -> int:
        """ Returns the index of the rotation/reflection setting currently selected on the object.

        Rotations and reflections are idx 2 and 3, respectively
        any other numbers will get a return value of 0.
        
        Order for rotations:
        up, down, left, right

        Order for reflections:
        none, horiz, vert, both

        Returns the index of these values based on the current properties of `self.obj`.

        this function is janky af
        """

        if self.selected_setting_idx not in [2, 3]:
            return 0

        enum_to_use = CameraConstants.OBJECT_ROTATIONS if self.selected_setting_idx == 2 else CameraConstants.OBJECT_REFLECTIONS
        property_to_use = self.obj.rotation if self.selected_setting_idx == 2 else self.obj.reflection

        enum_as_list = list(enum_to_use)
        for i in range(len(enum_as_list)):
            if enum_as_list[i].value == property_to_use:
                return i

        raise ValueError(f"[EditObjectPopup/get_selected_button_index]: Could not find matching enum member for obj property {property_to_use} in {enum_to_use} (self.selected_setting_idx={self.selected_setting_idx})")

    def handle_key(self, key: "Keystroke") -> Literal["close"] | None:
        """ Performs actions on this instance based on key pressed. Returns True if popup closed, False otherwise. """
        if key == "\x1b":
            return "close"
        elif key.name in ["KEY_TAB", "KEY_DOWN"]: # go down (forward) one row
            self.selected_setting_idx = (self.selected_setting_idx + 1) % 4
            self.selected_button_idx = self.get_selected_button_index()
        elif key.name in ["KEY_BTAB", "KEY_UP"]: # shift+tab; key code is \x1b[Z, go up (back) one row
            self.selected_setting_idx = (self.selected_setting_idx - 1) % 4
            self.selected_button_idx = self.get_selected_button_index()

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
        
        