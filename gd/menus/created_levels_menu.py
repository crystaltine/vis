import json
import os
from typing import List, Literal
from logger import Logger
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from gd_constants import GDConstants
from blessed.keyboard import Keystroke
from menus.MENU_GENERIC import GenericMenu
from render.utils import fcode_opt as fco


corner_deco_BL = TextureManager.compile_texture("./assets/menus/corner_deco.png")
corner_deco_BR = TextureManager.reflect_texture(corner_deco_BL, 'horizontal')
corner_deco_TL = TextureManager.reflect_texture(corner_deco_BL, 'vertical')
corner_deco_TR = TextureManager.reflect_texture(corner_deco_BL, 'both')

class CreatedLevelsMenu(GenericMenu):
    
    # curr_frame: CameraFrame | None = None

    # created_levels_index=0
    
    # # style constants
    # BG_COLOR = (63, 72, 204)
    # TITLE_COLOR = (129, 255, 90)
    # GROUND_MARGIN_TOP = 0.7 # ground at 70% of the screen
    # TITLE_MARGIN_TOP = 0.25
    # TITLE_MARGIN_BOTTOM = 0.08
    # BUTTON_GAP_X = 0.08
    # SIDE_BUTTON_SIZE_PX = 28 # px
    # MIDDLE_BUTTON_SIZE_PX = 28 # px

    frame: CameraFrame = None
    """ The frame that the level selector is drawn on. None until the init_level_selector is called at least once """
    
    created_levels_index = 0
    selected_option = 1
    """ Index of the currently selected level """

    PADDING_Y = 0.125
    PADDING_X = 0.15
    ARROW_BUTTON_PADDING_X_PX = 5 # IN PIXELS
    TOP_BOX_HEIGHT = 0.4
    
    PROGRESS_PADDINGS = 0.35 * (1 - TOP_BOX_HEIGHT - PADDING_Y)
    PROGRESS_GAP = 0.15 * (1 - TOP_BOX_HEIGHT - PADDING_Y)
    PROGRESS_BAR_HEIGHT = ((1 - TOP_BOX_HEIGHT - PADDING_Y) - 2*PROGRESS_PADDINGS - PROGRESS_GAP) / 2
    
    
    arrow_button_white_right = TextureManager.compile_texture("./assets/menus/arrow_button_white.png")
    arrow_button_white_right_outline = TextureManager.compile_texture("./assets/menus/arrow_button_white_outline.png")
    
    arrow_button_white_left = TextureManager.reflect_texture(arrow_button_white_right, 'horizontal')
    arrow_button_white_left_outline = TextureManager.reflect_texture(arrow_button_white_right_outline, 'horizontal')

    start_button = TextureManager.compile_texture("./assets/created_levels_menu/play_button.png")
    start_button_outline = TextureManager.compile_texture("./assets/created_levels_menu/play_button_outline.png")
    edit_button = TextureManager.compile_texture("./assets/created_levels_menu/edit_level_button.png")
    edit_button_outline = TextureManager.compile_texture("./assets/created_levels_menu/edit_level_button_outline.png")



    NORMAL_BAR_COLOR = (123, 255, 0)
    PRACTICE_BAR_COLOR = (140, 255, 251)

    def parse_created_levels_files() -> List:

        created_levels=[]

        path_to_json = 'levels/created'
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        
        for file in json_files:
            f = open(path_to_json+"/"+file)
            data = json.load(f)['metadata']
            created_levels.append({'name':data['name'], 'color':data['start_settings']['bg_color'], 
                        'path':'./'+path_to_json+'/'+file})

        return created_levels
    
    def indexof_level_with_name(name: str) -> int:
        """ Return the index of the level with the given name in the created_levels list, or -1 if not found """
        for i, level in enumerate(CreatedLevelsMenu.created_levels):
            if level['name'] == name:
                return i
        return -1
    
    created_levels=parse_created_levels_files()
    
    @classmethod
    def render(c):
        
        level_data = c.created_levels[c.created_levels_index]
        
        c.frame = CameraFrame()
        c.frame.fill(level_data['color'])
        
        # handy variables, derived from screen size and preset proportions
        left = int(c.PADDING_X*c.frame.width)
        top = int(c.PADDING_Y*c.frame.height)
        center = int(c.frame.width/2)
        width = int((1-2*c.PADDING_X)*c.frame.width)
        progbar_height = int(c.PROGRESS_BAR_HEIGHT*c.frame.height)
        normalbar_top = int((c.PADDING_Y + c.TOP_BOX_HEIGHT + c.PROGRESS_PADDINGS)*c.frame.height)
        practicebar_top = int((c.PADDING_Y + c.TOP_BOX_HEIGHT + c.PROGRESS_PADDINGS + c.PROGRESS_GAP + c.PROGRESS_BAR_HEIGHT)*c.frame.height)
        
        horiz_center = int(0.5 * c.frame.width)


        #title_center = int(CustomLevelsMenu.TITLE_MARGIN_TOP * new_frame.height + TextureManager.font_title.font_height/2)


        # draw main level box, a half-transparent black rect from:
        # (y1,x1) = (PADDING_Y, PADDING_X), width = 1-2*PADDING_X, height = TOP_BOX_HEIGHT
        c.frame.add_rect(
            (0, 0, 0, 128), 
            left,
            top,
            width,
            int(c.TOP_BOX_HEIGHT*c.frame.height)
        )
        
        # level name should thus be centered at PAD_Y + TOP_BOX_HEIGHT/2
        c.frame.add_text(
            c.frame.width//2,
            int(((c.PADDING_Y + c.TOP_BOX_HEIGHT)/2) * c.frame.height),
            TextureManager.font_title,
            level_data['name'],           
        )

        # draw buttons

        #middle_button_center_y = int((CreatedLevelsMenu.TITLE_MARGIN_TOP + CreatedLevelsMenu.TITLE_MARGIN_BOTTOM) * c.frame.height + TextureManager.font_title.font_height + CreatedLevelsMenu.MIDDLE_BUTTON_SIZE_PX/2)
        c.frame.add_pixels_centered_at(
            int(c.frame.width*0.15),
            int(c.frame.height*0.75),
            CreatedLevelsMenu.arrow_button_white_left if CreatedLevelsMenu.selected_option != 0 else CreatedLevelsMenu.arrow_button_white_left_outline
        )

        c.frame.add_pixels_centered_at(
            int(c.frame.width*0.35),
            int(c.frame.height*0.75),
            CreatedLevelsMenu.start_button if CreatedLevelsMenu.selected_option != 1 else CreatedLevelsMenu.start_button_outline
        )

        c.frame.add_pixels_centered_at(
            int(c.frame.width*0.65),
            int(c.frame.height*0.75),
            CreatedLevelsMenu.edit_button if CreatedLevelsMenu.selected_option != 2 else CreatedLevelsMenu.edit_button_outline
        )

        c.frame.add_pixels_centered_at(
            int(c.frame.width*0.85),
            int(c.frame.height*0.75),
            CreatedLevelsMenu.arrow_button_white_right if CreatedLevelsMenu.selected_option != 3 else CreatedLevelsMenu.arrow_button_white_right_outline
        )



        
        # #side_button_x_offset = int(CustomLevelsMenu.BUTTON_GAP_X * new_frame.width + CustomLevelsMenu.SIDE_BUTTON_SIZE_PX/2 + CustomLevelsMenu.MIDDLE_BUTTON_SIZE_PX/2)
        # c.frame.add_pixels_centered_at(
        #     horiz_center - side_button_x_offset,
        #     middle_button_center_y,
        #     CustomLevelsMenu.plus_button if CustomLevelsMenu.selected_option != 0 else CustomLevelsMenu.plus_button_outline
        # )
        
        # c.frame.add_pixels_centered_at(
        #     horiz_center + side_button_x_offset,
        #     middle_button_center_y,
        #     CustomLevelsMenu.online_button if CustomLevelsMenu.selected_option != 2 else CustomLevelsMenu.online_button_outline
        # )










        
        # # draw the arrow buttons
        # c.frame.add_pixels_centered_at(
        #     c.ARROW_BUTTON_PADDING_X_PX + arrow_button_white_left.shape[1]//2,
        #     c.frame.height//2,
        #     arrow_button_white_left,
        # )
        # c.frame.add_pixels_centered_at(
        #     c.frame.width - c.ARROW_BUTTON_PADDING_X_PX - arrow_button_white_right.shape[1]//2,
        #     c.frame.height//2,
        #     arrow_button_white_right,
        # )
        
        # add corner decos at the corners
        c.frame.add_pixels_topleft(0, 0, corner_deco_TL)
        c.frame.add_pixels_topleft(c.frame.width - corner_deco_TR.shape[1], 0, corner_deco_TR)
        c.frame.add_pixels_topleft(0, c.frame.height - corner_deco_BL.shape[0], corner_deco_BL)
        c.frame.add_pixels_topleft(c.frame.width - corner_deco_BR.shape[1], c.frame.height - corner_deco_BR.shape[0], corner_deco_BR)

        c.frame.render_raw()
        
        
        
    
    def get_selected_level_filepath():
        return CreatedLevelsMenu.created_levels[CreatedLevelsMenu.created_levels_index]['path']
    
    @classmethod
    def on_key(c, val: Keystroke) -> Literal["play_created_level"] | None:
        if val.name in ["KEY_LEFT", "KEY_BTAB"]:
            CreatedLevelsMenu.selected_option = (CreatedLevelsMenu.selected_option - 1) % 4
            # CreatedLevelsMenu.created_levels_index = (CreatedLevelsMenu.created_levels_index - 1) % len(CreatedLevelsMenu.created_levels)
            c.render()

        elif val.name in ["KEY_RIGHT", "KEY_TAB"]:
            CreatedLevelsMenu.selected_option = (CreatedLevelsMenu.selected_option + 1) % 4
            # CreatedLevelsMenu.created_levels_index = (CreatedLevelsMenu.created_levels_index + 1) % len(CreatedLevelsMenu.created_levels)
            c.render()

        elif val.name == "KEY_ENTER":
            
            if CreatedLevelsMenu.selected_option==0:
                CreatedLevelsMenu.created_levels_index = (CreatedLevelsMenu.created_levels_index - 1) % len(CreatedLevelsMenu.created_levels)
                c.render()
            
            elif CreatedLevelsMenu.selected_option==1:
                return 'play_created_level'
            
            elif CreatedLevelsMenu.selected_option==2:
                return 'edit_current_level'
            
            elif CreatedLevelsMenu.selected_option==3:
                CreatedLevelsMenu.created_levels_index = (CreatedLevelsMenu.created_levels_index + 1) % len(CreatedLevelsMenu.created_levels)
                c.render()

        
        