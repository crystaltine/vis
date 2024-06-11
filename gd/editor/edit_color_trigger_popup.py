from typing import Literal, TYPE_CHECKING, Callable, Tuple, Any

from logger import Logger
from render.texture_manager import TextureManager
from render.camera_frame import CameraFrame
from render.constants import CameraConstants
from gd_constants import GDConstants
if TYPE_CHECKING:
    from level import Level, LevelObject
    from blessed.keyboard import Keystroke

class EditColorTriggerPopup:
    """ A popup for editing a color trigger. """
    
    BG_COLOR = (147, 120, 78, 255)
    SELECTED_OPTION_BG_COLOR = (123, 102, 70, 255)
    OUTLINE_COLOR = (255, 255, 255, 255)
    FRACTION_OF_SCREEN_WIDTH = 0.4
    FRACTION_OF_SCREEN_HEIGHT = 0.65
    PADDING_Y = 5
    GAP_Y = 4
    PADDING_X = 4
    PADDING_SELECTION = 1
    SAVE_BUTTON_PAD_X = 3
    SAVE_BUTTON_PAD_Y = 1

    def __init__(
        self, 
        frame: "CameraFrame", 
        object: "LevelObject",
        level: "Level"):

        if object.type != "color_trigger":
            raise ValueError("EditColorTriggerPopup can only be created for color triggers.")
        
        self.target_channel = object.trigger_target
        """ Which color channel of the level this popup is editing.
        For color triggers, this determines which channel gets changed, for 
        level settings, this sets the default color for this color channel. 
        
        Available channels: "bg", "grnd", 1, 2, ...
        """
        
        self.object = object
        self.level = level
        
        
        self.inputs = [str(c) for c in object.trigger_color]
        """ Contains the state of the text inputs for each color channel. """
        
        self.make_legal()

        self.last_frame = frame

        self.selected_option = 0 
        """ 0 for editing channel#, 1 for R, 2 for G, 3 for B. represents which option the user is currently editing. """
        
        self.height = round(max(
            EditColorTriggerPopup.FRACTION_OF_SCREEN_HEIGHT * frame.height,
            TextureManager.font_small1.font_height*6 + EditColorTriggerPopup.PADDING_Y*2 + EditColorTriggerPopup.GAP_Y*5
            # be able to fit elements vertically
        ))
        
        # the preview square takes up all remamining space, after
        # the title and the channel input row.
        self.square_sidelen = self.height - TextureManager.font_small1.font_height*3 - EditColorTriggerPopup.PADDING_Y*2 - EditColorTriggerPopup.GAP_Y*3
        
        self.width = round(max(
            EditColorTriggerPopup.FRACTION_OF_SCREEN_WIDTH * frame.width,
            TextureManager.font_small1.font_width*11 + EditColorTriggerPopup.PADDING_X*2, # be able to fit title
            self.square_sidelen + EditColorTriggerPopup.PADDING_X*4 + TextureManager.font_small1.font_width*4 # be able to fit color labels, square, etc.
        ))
        
        self.left = int((frame.width - self.width) // 2)
        self.right = self.left + self.width
        self.horiz_center = int((self.left + self.right) // 2)
        self.top = int((frame.height - self.height) // 2)
        self.bottom = self.top + self.height
        self.vert_center = int((self.top + self.bottom) // 2)

    def render(self):
        """ Draws this popup to the center of the frame provided, and renders the frame. """

        #Logger.log(f"edit color pop: self.left={self.left}, self.top={self.top}")
        #Logger.log(f"{self.width=}, {self.height=}, {self.horiz_center=}, {self.vert_center=}")
        
        # add box and title
        new_frame = self.last_frame.copy()
        new_frame.add_rect(
            EditColorTriggerPopup.BG_COLOR,
            self.left, self.top, self.width, self.height,
            outline_color=EditColorTriggerPopup.OUTLINE_COLOR,
            outline_width=2,
            anchor="top-left"
        )
        new_frame.add_text(self.horiz_center, self.top + EditColorTriggerPopup.PADDING_Y, TextureManager.font_small1, "Color Trigger")
        
        # draw channel input row
        label_left = self.left + EditColorTriggerPopup.PADDING_X
        input_right = self.right - EditColorTriggerPopup.PADDING_X
        
        if self.selected_option == 0: # draw bg spanning from label_left-PADDING_SELECTION to input_right+PADDING_SELECTION
            new_frame.add_rect(
                EditColorTriggerPopup.SELECTED_OPTION_BG_COLOR,
                label_left-EditColorTriggerPopup.PADDING_SELECTION, 
                self.top+TextureManager.font_small1.font_height + EditColorTriggerPopup.PADDING_Y+EditColorTriggerPopup.GAP_Y-EditColorTriggerPopup.PADDING_SELECTION,
                input_right-label_left+EditColorTriggerPopup.PADDING_SELECTION*2, 
                TextureManager.font_small1.font_height+EditColorTriggerPopup.PADDING_SELECTION*2
            )
        text_center = self.top+TextureManager.font_small1.font_height + EditColorTriggerPopup.PADDING_Y + EditColorTriggerPopup.GAP_Y + TextureManager.font_small1.font_height // 2
        new_frame.add_text(label_left, text_center, TextureManager.font_small1, "Channel", anchor="left")
        new_frame.add_text(input_right, text_center, TextureManager.font_small1, str(self.target_channel), anchor="right")
        
        preview_square_top = self.top + TextureManager.font_small1.font_height*2 + EditColorTriggerPopup.PADDING_Y + EditColorTriggerPopup.GAP_Y*2
        
        # draw preview square
        new_frame.add_rect(
            self.get_color(),
            self.left+EditColorTriggerPopup.PADDING_X+1, 
            preview_square_top+1,
            self.square_sidelen-1, self.square_sidelen-1,
            outline_color=(255, 255, 255, 255),
            outline_width=1
        )
        
        # add color components numbers, all aligned right
        text_right = self.right - EditColorTriggerPopup.PADDING_X
        text_label_left = self.left + self.square_sidelen + EditColorTriggerPopup.PADDING_X*2
        
        # evenly split along the height of the preview square
        # the text takes up 3*font_height + 2*gap_y pixels
        # meaning there is (square_height - total_text_height) // 2 pixels above and below the text
        curr_text_top = preview_square_top + (self.square_sidelen - TextureManager.font_small1.font_height*3 - EditColorTriggerPopup.GAP_Y*2) // 2
        curr_text_center = curr_text_top + TextureManager.font_small1.font_height // 2
        if self.selected_option == 1: # draw bg spanning from text_label_left-PADDING_SELECTION to right+PADDING_SELECTION
            new_frame.add_rect(
                EditColorTriggerPopup.SELECTED_OPTION_BG_COLOR,
                text_label_left-EditColorTriggerPopup.PADDING_SELECTION, curr_text_top-EditColorTriggerPopup.PADDING_SELECTION,
                text_right-text_label_left+EditColorTriggerPopup.PADDING_SELECTION*2, TextureManager.font_small1.font_height+EditColorTriggerPopup.PADDING_SELECTION*2
            )
        new_frame.add_text(text_label_left, curr_text_center, TextureManager.font_small1, "R", anchor="left", color=(255, 192, 192))
        new_frame.add_text(text_right, curr_text_center, TextureManager.font_small1, self.inputs[0], anchor="right")
        
        curr_text_top += TextureManager.font_small1.font_height + EditColorTriggerPopup.GAP_Y
        curr_text_center = curr_text_top + TextureManager.font_small1.font_height // 2
        if self.selected_option == 2: # draw bg spanning from text_label_left-PADDING_SELECTION to right+PADDING_SELECTION
            new_frame.add_rect(
                EditColorTriggerPopup.SELECTED_OPTION_BG_COLOR,
                text_label_left-EditColorTriggerPopup.PADDING_SELECTION, curr_text_top-EditColorTriggerPopup.PADDING_SELECTION,
                text_right-text_label_left+EditColorTriggerPopup.PADDING_SELECTION*2, TextureManager.font_small1.font_height+EditColorTriggerPopup.PADDING_SELECTION*2
            )
        new_frame.add_text(text_label_left, curr_text_center, TextureManager.font_small1, "G", anchor="left", color=(192, 255, 192))
        new_frame.add_text(text_right, curr_text_center, TextureManager.font_small1, self.inputs[1], anchor="right")
        
        curr_text_top += TextureManager.font_small1.font_height + EditColorTriggerPopup.GAP_Y
        curr_text_center = curr_text_top + TextureManager.font_small1.font_height // 2
        if self.selected_option == 3: # draw bg spanning from text_label_left-PADDING_SELECTION to right+PADDING_SELECTION
            new_frame.add_rect(
                EditColorTriggerPopup.SELECTED_OPTION_BG_COLOR,
                text_label_left-EditColorTriggerPopup.PADDING_SELECTION, curr_text_top-EditColorTriggerPopup.PADDING_SELECTION,
                text_right-text_label_left+EditColorTriggerPopup.PADDING_SELECTION*2, TextureManager.font_small1.font_height+EditColorTriggerPopup.PADDING_SELECTION*2
            )
        new_frame.add_text(text_label_left, curr_text_center, TextureManager.font_small1, "B", anchor="left", color=(192, 192, 255))
        new_frame.add_text(text_right, curr_text_center, TextureManager.font_small1, self.inputs[2], anchor="right")

        # draw "Save" button at bottom
        text_center_y = self.bottom - TextureManager.font_small1.font_height//2 - EditColorTriggerPopup.PADDING_Y
        new_frame.add_rect(
            (95, 210, 91, 255),
            self.horiz_center,
            text_center_y,
            TextureManager.font_small1.get_width_of(2) + EditColorTriggerPopup.SAVE_BUTTON_PAD_X*2,
            TextureManager.font_small1.font_height + EditColorTriggerPopup.SAVE_BUTTON_PAD_Y*2,
            anchor="center",
            outline_width=int(self.selected_option == 4),
            outline_color=(255, 255, 255, 255)
        )
        new_frame.add_text(self.horiz_center, text_center_y, TextureManager.font_small1, "Ok", anchor="center")
        

        new_frame.render(self.last_frame)
        self.last_frame = new_frame

    def get_color(self) -> CameraConstants.RGBTuple:
        """ Returns the current color (specified by self.inputs) as an RGB tuple. DOES NOT CHECK FOR VALIDITY. """
        return tuple(int(c) for c in self.inputs)
    
    def make_legal(self):
        """ 
        Ensures that the current color is legal, by clipping each channel to [0, 255]. 
        
        If any input is not int-convertible, it is set to 0.
        """
        for i, c in enumerate(self.inputs):
            try:
                self.inputs[i] = str(max(0, min(255, int(c))))
            except ValueError:
                self.inputs[i] = "0"
                
    def get_next_channel(self) -> Literal["bg", "grnd"] | int:
        """ Returns the next channel to edit, based on the current channel. """
        if self.target_channel == "bg":
            return "grnd"
        elif self.target_channel == "grnd":
            return 1
        else:
            return self.target_channel + 1
        
    def get_prev_channel(self) -> Literal["bg", "grnd"] | int:
        """ Returns the previous channel to edit, based on the current channel. """
        if self.target_channel in ['bg', 'grnd']:
            return "bg"
        elif self.target_channel == 1:
            return "grnd"
        else:
            return self.target_channel - 1

    def handle_key(self, key: "Keystroke") -> Literal["close"] | None:
        """ Performs actions on this instance based on key pressed. Returns True if popup closed, False otherwise. """
        if key.name == "KEY_ESCAPE":
            return "close"
        
        elif key.name in ["KEY_TAB", "KEY_DOWN"]: # go down (forward) one row
            self.selected_option = (self.selected_option + 1) % 5
            
        elif key.name == "KEY_ENTER" and self.selected_option == 4: # save button
            self.level.edit_color_trigger_at(self.object.x, self.object.y, self.target_channel, self.get_color())
            self.object.trigger_target = self.target_channel
            self.object.trigger_color = self.get_color()
            return "close"
        
        elif key.name in ["KEY_BTAB", "KEY_UP"]: # shift+tab; key code is \x1b[Z, go up (back) one row
            self.selected_option = (self.selected_option - 1) % 5

        # L/R arrow keys - change the currently selected button
        elif key.name == "KEY_RIGHT":
            if self.selected_option == 0:
                self.target_channel = self.get_next_channel()
                    
            elif 0 < self.selected_option < 4:
                curr_channel = self.inputs[self.selected_option-1]
                self.inputs[self.selected_option-1] = str(int(curr_channel) + 1)
                self.make_legal()
            
        elif key.name == "KEY_LEFT":
            if self.selected_option == 0:
                self.target_channel = self.get_prev_channel()
                
            elif 0 < self.selected_option < 4:
                curr_channel = self.inputs[self.selected_option-1]
                self.inputs[self.selected_option-1] = str(int(curr_channel) - 1)
                self.make_legal()


        # if backspace, remove last character from current input (only if editing rgb)
        elif key.name == "KEY_BACKSPACE" and 0 < self.selected_option < 4:
            self.inputs[self.selected_option-1] = self.inputs[self.selected_option-1][:-1]
            self.make_legal()
            
        if key.isdigit() and 0 < self.selected_option < 4:
            self.inputs[self.selected_option-1] += key
            self.make_legal()
            
        self.render()
    