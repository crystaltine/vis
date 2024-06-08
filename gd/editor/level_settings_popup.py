from typing import Literal, TYPE_CHECKING, Callable, Tuple, Any
import os

from logger import Logger
from render.texture_manager import TextureManager
from render.camera_frame import CameraFrame
from render.constants import CameraConstants
from draw_utils import print2
from render.utils import fcode_opt as fco
from gd_constants import GDConstants


if TYPE_CHECKING:
    from level import Level
    from blessed.keyboard import Keystroke

class LevelSettingsPopup:
    """ A popup for editing a level's settings/default colors """
    
    BG_COLOR = (147, 120, 78, 255)
    SELECTED_OPTION_BG_COLOR = (123, 102, 70, 255)
    OUTLINE_COLOR = (255, 255, 255, 255)
    FRACTION_OF_SCREEN_WIDTH = 0.7
    FRACTION_OF_SCREEN_HEIGHT = 0.9
    PADDING_Y = 5
    GAP_Y = 7
    PADDING_X = 4
    BUTTON_PADDING_X = 3
    BUTTON_PADDING_Y = 1

    def __init__(self, frame: "CameraFrame", level: "Level"):

        self.level = level
        
        self.curr_input = level.metadata["song_filepath"]
        """ Contains the state of the current input. Updates field on level obj as user types. """
        
        self.last_frame = frame

        self.selected_option = 0 
        """ 0 for song input, 1 for edit color chnls btn, 2 for Save&back, 3 for Save&Close editor """
        
        self.height = round(max(
            LevelSettingsPopup.FRACTION_OF_SCREEN_HEIGHT * frame.height,
            TextureManager.font_small1.font_height*5 + LevelSettingsPopup.PADDING_Y*2 + LevelSettingsPopup.GAP_Y*4 
            # be able to fit elements vertically
        ))

        self.width = round(max(
            LevelSettingsPopup.FRACTION_OF_SCREEN_WIDTH * frame.width,
            TextureManager.font_small1.get_width_of(18) + LevelSettingsPopup.PADDING_X*2, # be able to fit longest str: "Save & Close Editor"
        ))
        
        self.left = int((frame.width - self.width) // 2)
        self.right = self.left + self.width
        self.horiz_center = int((self.left + self.right) // 2)
        self.top = int((frame.height - self.height) // 2)
        self.bottom = self.top + self.height
        self.vert_center = int((self.top + self.bottom) // 2)

    def render(self):
        """ Draws this popup to the center of the frame provided, and renders the frame. """

        text_leftmost = self.left + LevelSettingsPopup.PADDING_X
        text_rightmost = self.right - LevelSettingsPopup.PADDING_X
        #Logger.log(f"edit color pop: self.left={self.left}, self.top={self.top}")
        #Logger.log(f"{self.width=}, {self.height=}, {self.horiz_center=}, {self.vert_center=}")
        
        # add box and title
        new_frame = self.last_frame.copy()
        new_frame.add_rect(
            LevelSettingsPopup.BG_COLOR,
            self.left, self.top, self.width, self.height,
            outline_color=LevelSettingsPopup.OUTLINE_COLOR,
            outline_width=2,
            anchor="top-left"
        )
        new_frame.add_text(self.horiz_center, self.top + LevelSettingsPopup.PADDING_Y, TextureManager.font_small1, "Level Settings")
        
        ######## SONG FILENAME OPTION
        text_center_y = self.top+TextureManager.font_small1.font_height + LevelSettingsPopup.PADDING_Y + LevelSettingsPopup.GAP_Y + TextureManager.font_small1.font_height // 2
        filepath_text_center_y = text_center_y # USED LATER WHEN WE PRINT DOWN BELOW
        new_frame.add_text(text_leftmost, text_center_y, TextureManager.font_small1, "Song Filename", anchor="left")
        new_frame.add_rect(
            LevelSettingsPopup.SELECTED_OPTION_BG_COLOR,
            text_rightmost,
            text_center_y,
            40, 3*2,
            anchor="right",
            outline_width=int(self.selected_option == 0),
            outline_color=(255, 255, 255, 255)
        )
        
        ######## COLOR CHANNELS OPTION
        text_center_y += TextureManager.font_small1.font_height + LevelSettingsPopup.GAP_Y
        new_frame.add_text(text_leftmost, text_center_y, TextureManager.font_small1, "Edit Colors", anchor="left")
        new_frame.add_rect(
            (95, 210, 91, 255),
            text_rightmost,
            text_center_y,
            TextureManager.font_small1.get_width_of(4) + LevelSettingsPopup.BUTTON_PADDING_X*2,
            TextureManager.font_small1.font_height + LevelSettingsPopup.BUTTON_PADDING_Y*2,
            anchor="right",
            outline_width=int(self.selected_option == 1),
            outline_color=(255, 255, 255, 255)
        )
        new_frame.add_text(text_rightmost-LevelSettingsPopup.BUTTON_PADDING_X, text_center_y, TextureManager.font_small1, "Open", anchor="right")
        
        ######## SAVE & BACK OPTION
        text_center_y += TextureManager.font_small1.font_height + LevelSettingsPopup.GAP_Y
        #new_frame.add_text(text_leftmost, text_center_y, TextureManager.font_small1, "Save & Back", anchor="left")
        new_frame.add_rect(
            (95, 210, 91, 255),
            text_rightmost,
            text_center_y,
            TextureManager.font_small1.get_width_of(11) + LevelSettingsPopup.BUTTON_PADDING_X*2,
            TextureManager.font_small1.font_height + LevelSettingsPopup.BUTTON_PADDING_Y*2,
            anchor="right",
            outline_width=int(self.selected_option == 2),
            outline_color=(255, 255, 255, 255)
        )
        new_frame.add_text(text_rightmost-LevelSettingsPopup.BUTTON_PADDING_X, text_center_y, TextureManager.font_small1, "Save & Back", anchor="right")
        
        ######## SAVE & CLOSE EDITOR OPTION
        text_center_y += TextureManager.font_small1.font_height + LevelSettingsPopup.GAP_Y
        #new_frame.add_text(text_leftmost, text_center_y, TextureManager.font_small1, "Save & Close Editor", anchor="left")
        new_frame.add_rect(
            (228, 87, 68, 255),
            text_rightmost,
            text_center_y,
            TextureManager.font_small1.get_width_of(18) + LevelSettingsPopup.BUTTON_PADDING_X*2,
            TextureManager.font_small1.font_height + LevelSettingsPopup.BUTTON_PADDING_Y*2,
            anchor="right",
            outline_width=int(self.selected_option == 3),
            outline_color=(255, 255, 255, 255)
        )
        new_frame.add_text(text_rightmost-LevelSettingsPopup.BUTTON_PADDING_X, text_center_y, TextureManager.font_small1, "Save & Exit Editor", anchor="right")

        new_frame.render(self.last_frame)
        
        # print the current input content
        fcode = fco((255, 255, 255), LevelSettingsPopup.SELECTED_OPTION_BG_COLOR)
        term_loc = GDConstants.term.move_xy(text_rightmost-len(self.curr_input)-1, round(filepath_text_center_y/2))
        print2(term_loc + fcode + self.curr_input)

    def handle_key(self, key: "Keystroke") -> Literal["open-colors", "save-quit", "close"] | None:
        """ Performs actions on this instance based on key pressed. Returns True if popup closed, False otherwise. """
        if key.name == "KEY_ESCAPE":
            return "close"
        elif key.name in ["KEY_TAB", "KEY_DOWN"]: # go down (forward) one row
            self.selected_option = (self.selected_option + 1) % 4
        elif key.name in ["KEY_BTAB", "KEY_UP"]: # shift+tab; key code is \x1b[Z, go up (back) one row
            self.selected_option = (self.selected_option - 1) % 4

        elif key.name == "KEY_ENTER":
            if self.selected_option == 0:
                self.selected_option = 1 # just go to next option
            elif self.selected_option == 1:
                return "open-colors"
            elif self.selected_option == 2:
                return "close"
            elif self.selected_option == 3:
                return "save-quit"

        # catch all for typing in the song filepath
        if key.name == "KEY_BACKSPACE":
            self.curr_input = self.curr_input[:-1]
            
            # redraw the input box
            new_frame = self.last_frame.copy()
            temp_color = [c+1 for c in LevelSettingsPopup.SELECTED_OPTION_BG_COLOR[:3]]
            new_frame.add_rect(
                temp_color, # very stupid, but forces the frame to rerender this, covering
                # up the printed text from the last frame.
                self.right - LevelSettingsPopup.PADDING_X,
                self.top+TextureManager.font_small1.font_height + LevelSettingsPopup.PADDING_Y + LevelSettingsPopup.GAP_Y + TextureManager.font_small1.font_height // 2,
                40, 3*2,
                anchor="right",
                outline_width=int(self.selected_option == 0),
                outline_color=(255, 255, 255, 255)
            )
            new_frame.render(self.last_frame)
            self.last_frame = new_frame
        
        # if alphanumeric, space, or symbol, add to input
        elif key.isalnum() or key.isprintable():
            if self.selected_option == 0:
                self.curr_input += key
                self.level.metadata["song_filepath"] = self.curr_input

        self.render()
