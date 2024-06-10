from typing import TypedDict, Tuple, Literal
from logger import Logger
#from bottom_menu import *
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from draw_utils import print2
from render.utils import fcode_opt as fco
from blessed.keyboard import Keystroke
import os, json
from gd_constants import GDConstants
from menus.MENU_GENERIC import GenericMenu

class LevelPreviewData(TypedDict):
    name: str
    color: Tuple[int, int, int]
    path: str
    progress_normal: float
    progress_practice: float

arrow_button_white_right = TextureManager.compile_texture("./assets/menus/arrow_button_white.png")
arrow_button_white_left = TextureManager.reflect_texture(arrow_button_white_right, 'horizontal')
corner_deco_BL = TextureManager.compile_texture("./assets/menus/corner_deco.png")
corner_deco_BR = TextureManager.reflect_texture(corner_deco_BL, 'horizontal')
corner_deco_TL = TextureManager.reflect_texture(corner_deco_BL, 'vertical')
corner_deco_TR = TextureManager.reflect_texture(corner_deco_BL, 'both')

class OfficialLevelsMenu(GenericMenu):
    """ Level selector page for the OFFICIAL levels menu """
    
    frame: CameraFrame = None
    """ The frame that the level selector is drawn on. None until the init_level_selector is called at least once """
    
    selected_level_idx = 0
    """ Index of the currently selected level """

    PADDING_Y = 0.125
    PADDING_X = 0.15
    ARROW_BUTTON_PADDING_X_PX = 5 # IN PIXELS
    TOP_BOX_HEIGHT = 0.4
    
    PROGRESS_PADDINGS = 0.35 * (1 - TOP_BOX_HEIGHT - PADDING_Y)
    PROGRESS_GAP = 0.15 * (1 - TOP_BOX_HEIGHT - PADDING_Y)
    PROGRESS_BAR_HEIGHT = ((1 - TOP_BOX_HEIGHT - PADDING_Y) - 2*PROGRESS_PADDINGS - PROGRESS_GAP) / 2
    
    NORMAL_BAR_COLOR = (123, 255, 0)
    PRACTICE_BAR_COLOR = (140, 255, 251)
    
    def parse_level_files():

        levels=[]

        path_to_json = 'levels/official'
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        
        for file in json_files:
            f = open('levels/official/'+file)
            data = json.load(f)['metadata']
            levels.append(
                {
                    'name':data['name'], 
                    'color':data['start_settings']['bg_color'], 
                    'path':'./levels/official/'+file, 
                    'progress_normal':data['progress_normal'],
                    'progress_practice':data['progress_practice']
                }
            )

        return levels
    
    levels = parse_level_files()

    @classmethod
    def render(c):
        
        level_data = c.levels[c.selected_level_idx]
        
        Logger.log(f"rendering officl level menu, selected idx: {c.selected_level_idx}, level_data: {level_data}")
        
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
        
        # PROGRESS BARS
        
        normal_text = f"    Normal: {int(level_data['progress_normal']*100)}%    " # spacing for a bit of padding
        practice_text = f"    Practice: {int(level_data['progress_practice']*100)}%    "
        
        # start drawing the bg of normal progress bar at bottom of main box + progress padding
        # which is at c.PADDING_Y + c.TOP_BOX_HEIGHT + c.PROGRESS_PADDINGS of the screen
        c.frame.add_rect(
            (0, 0, 0, 128),
            left,
            normalbar_top,
            width,
            progbar_height,
            outline_width=1,
            outline_color=(0, 0, 0, 128)
        )
        c.frame.add_rect(
            c.NORMAL_BAR_COLOR,
            left,
            normalbar_top,
            int(level_data['progress_normal']*width),
            progbar_height
        )
        
        # PRACTICE BAR
        c.frame.add_rect(
            (0, 0, 0, 128),
            left,
            practicebar_top,
            width,
            progbar_height,
            outline_width=1,
            outline_color=(0, 0, 0, 128)
        )
        c.frame.add_rect(
            c.PRACTICE_BAR_COLOR,
            left,
            practicebar_top,
            int(level_data['progress_practice']*width),
            progbar_height
        )

        # draw the arrow buttons
        c.frame.add_pixels_centered_at(
            c.ARROW_BUTTON_PADDING_X_PX + arrow_button_white_left.shape[1]//2,
            c.frame.height//2,
            arrow_button_white_left,
        )
        c.frame.add_pixels_centered_at(
            c.frame.width - c.ARROW_BUTTON_PADDING_X_PX - arrow_button_white_right.shape[1]//2,
            c.frame.height//2,
            arrow_button_white_right,
        )
        
        # add corner decos at the corners
        c.frame.add_pixels_topleft(0, 0, corner_deco_TL)
        c.frame.add_pixels_topleft(c.frame.width - corner_deco_TR.shape[1], 0, corner_deco_TR)
        c.frame.add_pixels_topleft(0, c.frame.height - corner_deco_BL.shape[0], corner_deco_BL)
        c.frame.add_pixels_topleft(c.frame.width - corner_deco_BR.shape[1], c.frame.height - corner_deco_BR.shape[0], corner_deco_BR)

        c.frame.render_raw()
        # now add text
        halfdark_level_color = (level_data['color'][0]//2, level_data['color'][1]//2, level_data['color'][2]//2)
        text_fcode = fco((255, 255, 255), halfdark_level_color)
        print2(GDConstants.term.move_xy(center - len(normal_text)//2, (normalbar_top - 4)//2) + text_fcode+normal_text)
        print2(GDConstants.term.move_xy(center - len(practice_text)//2, (practicebar_top - 4)//2) + text_fcode+practice_text)
    
    def update_level_progress(filepath: str, new_value: float, key: Literal["normal", "practice"]):
        """ Update the progress field of the metadata in the levels field of this class (not the file, thats handled in game.py) """
    
        Logger.log("Updating level progress in mem, filepath: "+filepath+" key: "+key+" new_value: "+str(new_value))
    
        for level in OfficialLevelsMenu.levels:
            if level['path'] == filepath:
                Logger.log(f"ladies and gentlemen, we got him: {level['name']}")
                level[key] = new_value
                break
    
    def get_selected_level_filepath():
        return OfficialLevelsMenu.levels[OfficialLevelsMenu.selected_level_idx]['path']
    
    @classmethod
    def on_key(c, val: Keystroke) -> Literal["play_level"] | None:
        if val.name in ["KEY_LEFT", "KEY_BTAB"]:
            OfficialLevelsMenu.selected_level_idx = (OfficialLevelsMenu.selected_level_idx - 1) % len(OfficialLevelsMenu.levels)
            c.render()
            
        elif val.name in ["KEY_RIGHT", "KEY_TAB"]:
            OfficialLevelsMenu.selected_level_idx = (OfficialLevelsMenu.selected_level_idx + 1) % len(OfficialLevelsMenu.levels)
            c.render()

        elif val.name == "KEY_ENTER":
            return 'play_level' # menuhandler can use cls.selected_level_idx to get the level to play

        
        
    