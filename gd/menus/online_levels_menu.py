from typing import Literal
from logger import Logger
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from gd_constants import GDConstants
from blessed.keyboard import Keystroke
from menus.MENU_GENERIC import GenericMenu

corner_deco_BL = TextureManager.compile_texture("./assets/menus/corner_deco.png")
corner_deco_BR = TextureManager.reflect_texture(corner_deco_BL, 'horizontal')
corner_deco_TL = TextureManager.reflect_texture(corner_deco_BL, 'vertical')
corner_deco_TR = TextureManager.reflect_texture(corner_deco_BL, 'both')

class OnlineLevelsMenu(GenericMenu):
    
    curr_frame: CameraFrame | None = None
    
    # style constants
    BG_COLOR = (63, 72, 204)
    TITLE_COLOR = (129, 255, 90)
    GROUND_MARGIN_TOP = 0.7 # ground at 70% of the screen
    TITLE_MARGIN_TOP = 0.25
    TITLE_MARGIN_BOTTOM = 0.08
    BUTTON_GAP_X = 0.08
    SIDE_BUTTON_SIZE_PX = 28 # px
    MIDDLE_BUTTON_SIZE_PX = 28 # px
    
    def render():
        new_frame = CameraFrame()
        new_frame.fill((OnlineLevelsMenu.BG_COLOR))

        horiz_center = int(0.5 * new_frame.width)
        title_center = int(OnlineLevelsMenu.TITLE_MARGIN_TOP * new_frame.height + TextureManager.font_title.font_height/2)
        
        # draw title text
        new_frame.add_text(horiz_center, title_center, TextureManager.font_title, "Online Levels", color=OnlineLevelsMenu.TITLE_COLOR)
        
        # TODO
        new_frame.add_text(horiz_center, title_center + TextureManager.font_title.font_height + 2, TextureManager.font_title, "Coming Soon!", color=OnlineLevelsMenu.TITLE_COLOR)
        
        # add corner decos at the corners
        new_frame.add_pixels_topleft(0, 0, corner_deco_TL)
        new_frame.add_pixels_topleft(new_frame.width - corner_deco_TR.shape[1], 0, corner_deco_TR)
        new_frame.add_pixels_topleft(0, new_frame.height - corner_deco_BL.shape[0], corner_deco_BL)
        new_frame.add_pixels_topleft(new_frame.width - corner_deco_BR.shape[1], new_frame.height - corner_deco_BR.shape[0], corner_deco_BR)
        
        if OnlineLevelsMenu.curr_frame is not None:
            new_frame.render(OnlineLevelsMenu.curr_frame)
        else: 
            new_frame.render_raw()
        
    def on_key(val: Keystroke) -> None:
        # TODO
        return None

        
        