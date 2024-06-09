from typing import Literal
from logger import Logger
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from gd_constants import GDConstants
from blessed.keyboard import Keystroke
from menus.MENU_GENERIC import GenericMenu
from level import Level
import os

corner_deco_BL = TextureManager.compile_texture("./assets/menus/corner_deco.png")
corner_deco_BR = TextureManager.reflect_texture(corner_deco_BL, 'horizontal')
corner_deco_TL = TextureManager.reflect_texture(corner_deco_BL, 'vertical')
corner_deco_TR = TextureManager.reflect_texture(corner_deco_BL, 'both')

class CreateLevelMenu(GenericMenu):
    
    curr_frame: CameraFrame | None = None
    
    selected_option_idx: int = 0
    """ Index of the currently selected option, 0 for editing name, 1 for save button, 2 for cancel button """
    curr_input: str = "Untitled"
    levelname_taken: bool = False
    
    # style constants
    BG_COLOR = (63, 72, 204)
    BG_COLOR_2 = (29, 37, 143)
    INPUT_BG_COLOR = (0, 0, 0, 64)
    INPUT_BG_COLOR_SELECTED = (0, 0, 0, 144)
    TITLE_COLOR = (129, 255, 90)
    CREATE_BUTTON_COLOR = (95, 210, 91)
    CREATE_BUTTON_DISABLED_COLOR = (144, 163, 144)
    CANCEL_BUTTON_COLOR = (219, 96, 58)
    INPUT_BOX_LENGTH = 0.8
    TITLE_MARGIN_TOP = 0.25
    TITLE_MARGIN_BOTTOM = 0.1
    OPTION_GAP = 0.07
    
    INPUT_PADDING_Y = 3 # px
    INPUT_PADDING_X = 5 # px
    BUTTON_PADDING_Y = 1 # px
    BUTTON_PADDING_X = 5 # px
    
    def render():
        new_frame = CameraFrame()
        new_frame.fill_with_gradient(CreateLevelMenu.BG_COLOR_2, CreateLevelMenu.BG_COLOR, "vertical")

        horiz_center = int(0.5 * new_frame.width)
        title_center = int(CreateLevelMenu.TITLE_MARGIN_TOP*new_frame.height+TextureManager.font_title.font_height/2)
        
        # draw title text
        new_frame.add_text(horiz_center, title_center, TextureManager.font_title, "Create New Level", color=CreateLevelMenu.TITLE_COLOR)
        
        # input box for name of the level
        input_text_center = int((CreateLevelMenu.TITLE_MARGIN_TOP + CreateLevelMenu.TITLE_MARGIN_BOTTOM)*new_frame.height+TextureManager.font_title.font_height+TextureManager.font_small1.font_height/2)
        
        # draw rect around with padding
        input_box_height = TextureManager.font_small1.font_height + 2*CreateLevelMenu.INPUT_PADDING_Y
        input_box_width = int(max(
            TextureManager.font_title.get_width_of(len(CreateLevelMenu.curr_input)) + 2*CreateLevelMenu.INPUT_PADDING_X,
            CreateLevelMenu.INPUT_BOX_LENGTH*new_frame.width
        ))
        
        new_frame.add_rect(
            CreateLevelMenu.INPUT_BG_COLOR_SELECTED if CreateLevelMenu.selected_option_idx == 0 else CreateLevelMenu.INPUT_BG_COLOR,
            horiz_center, 
            input_text_center, 
            input_box_width, 
            input_box_height, 
            anchor="center",
            outline_width=CreateLevelMenu.selected_option_idx == 0,
            outline_color=(255, 255, 255)
        )
        new_frame.add_text(horiz_center, input_text_center, TextureManager.font_small1, CreateLevelMenu.curr_input)
        
        # add cancel and save buttons
        create_button_text = "Create" if not CreateLevelMenu.levelname_taken else "Name Taken!"
        curr_center_y = int(input_text_center + TextureManager.font_small1.font_height + CreateLevelMenu.OPTION_GAP*new_frame.height)
        new_frame.add_rect(
            CreateLevelMenu.CREATE_BUTTON_COLOR if not CreateLevelMenu.levelname_taken else CreateLevelMenu.CREATE_BUTTON_DISABLED_COLOR,
            horiz_center,
            curr_center_y,
            TextureManager.font_small1.get_width_of(len(create_button_text)) + CreateLevelMenu.BUTTON_PADDING_X*2,
            TextureManager.font_small1.font_height + CreateLevelMenu.BUTTON_PADDING_Y*2,
            anchor="center",
            outline_width=int(CreateLevelMenu.selected_option_idx == 1),
            outline_color=(255, 255, 255, 255) if not CreateLevelMenu.levelname_taken else (255, 255, 255, 128)
        )
        new_frame.add_text(horiz_center, curr_center_y, TextureManager.font_small1, create_button_text)
        
        # Cancel button
        curr_center_y += int(TextureManager.font_small1.font_height + CreateLevelMenu.OPTION_GAP*new_frame.height)
        new_frame.add_rect(
            CreateLevelMenu.CANCEL_BUTTON_COLOR,
            horiz_center,
            curr_center_y,
            TextureManager.font_small1.get_width_of(6) + CreateLevelMenu.BUTTON_PADDING_X*2,
            TextureManager.font_small1.font_height + CreateLevelMenu.BUTTON_PADDING_Y*2,
            anchor="center",
            outline_width=int(CreateLevelMenu.selected_option_idx == 2),
            outline_color=(255, 255, 255, 255)
        )
        new_frame.add_text(horiz_center, curr_center_y, TextureManager.font_small1, "Cancel")
              
        # add corner decos at the corners
        new_frame.add_pixels_topleft(0, 0, corner_deco_TL)
        new_frame.add_pixels_topleft(new_frame.width - corner_deco_TR.shape[1], 0, corner_deco_TR)
        new_frame.add_pixels_topleft(0, new_frame.height - corner_deco_BL.shape[0], corner_deco_BL)
        new_frame.add_pixels_topleft(new_frame.width - corner_deco_BR.shape[1], new_frame.height - corner_deco_BR.shape[0], corner_deco_BR)
        
        if CreateLevelMenu.curr_frame is not None:
            new_frame.render(CreateLevelMenu.curr_frame)
        else: 
            new_frame.render_raw()
    
    def check_if_levelname_taken() -> bool:
        """ Check if the current level name is already taken """
        return os.path.exists(f"./levels/created/{CreateLevelMenu.curr_input}.json")
       
    def on_key(val: Keystroke) -> None:
        if val.name in ["KEY_TAB", "KEY_DOWN"]: # go down (forward) one row
            CreateLevelMenu.selected_option_idx = (CreateLevelMenu.selected_option_idx + 1) % 3
            CreateLevelMenu.levelname_taken = CreateLevelMenu.check_if_levelname_taken()
            
        elif val.name in ["KEY_BTAB", "KEY_UP"]: # shift+tab; key code is \x1b[Z, go up (back) one row
            CreateLevelMenu.selected_option_idx = (CreateLevelMenu.selected_option_idx - 1) % 3
            CreateLevelMenu.levelname_taken = CreateLevelMenu.check_if_levelname_taken()

        if val.name == "KEY_ENTER":
            if CreateLevelMenu.selected_option_idx == 0:
                CreateLevelMenu.selected_option_idx = 1 # just go to next option
                CreateLevelMenu.levelname_taken = CreateLevelMenu.check_if_levelname_taken()
                
            elif CreateLevelMenu.selected_option_idx == 1:
                if not CreateLevelMenu.levelname_taken:
                    Level.create_new_file(CreateLevelMenu.curr_input)
                    return "goto_created_levels_menu"
                # else, do nothing (button is disabled)
            elif CreateLevelMenu.selected_option_idx == 2:
                return "goto_custom_levels_menu"

        # catch all for typing in the song filepath
        if CreateLevelMenu.selected_option_idx == 0:
            if val.name == "KEY_BACKSPACE":
                CreateLevelMenu.curr_input = CreateLevelMenu.curr_input[:-1]
                CreateLevelMenu.levelname_taken = CreateLevelMenu.check_if_levelname_taken()
                
            # if alphanumeric, space, or symbol, add to input
            elif val.isalnum() or val.isprintable():
                CreateLevelMenu.curr_input += val
                CreateLevelMenu.levelname_taken = CreateLevelMenu.check_if_levelname_taken()

        CreateLevelMenu.render()
