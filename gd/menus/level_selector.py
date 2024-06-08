from typing import TypedDict, Tuple
from logger import Logger
from bottom_menu import *
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from draw_utils import print2
from render.utils import fcode_opt as fco

os.system('cls')

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

class LevelSelector:
    """ Level selector page for the MAIN levels menu """
    
    frame: CameraFrame = None
    """ The frame that the level selector is drawn on. None until the init_level_selector is called at least once """
    
    # NOTE - this should eventually be autoloaded from the levels directory, this is just for tests
    levels = [
        {
            'name':'Stereo Madness',
            'color': (63, 72, 210),
            'path': './levels/official/stereo_madness.json',
            'progress_normal': 0.95,
            'progress_practice': 1,
        },
        {
            'name':'Back On Track',
            'color': (223, 45, 180),
            'path': './levels/created3.json',
            'progress_normal': 0.58,
            'progress_practice': 0.26,
        }, 
        {
            'name':'Polargeist',
            'color': (92, 215, 62),
            'path': './levels/created3.json',
            'progress_normal': 1,
            'progress_practice': 1,
        }, 
        {
            'name':'Dry Out',
            'color': (154, 73, 19),
            'path': './levels/created3.json',
            'progress_normal': 0.36,
            'progress_practice': 1,
        }, 
        {
            'name':'Base After Base',
            'color': (225, 184, 71),
            'path': './levels/created3.json',
            'progress_normal': 0.05,
            'progress_practice': 0.78,
        }, 
        {
            'name':'Cant Let Go',
            'color': (254, 246, 29),
            'path': './levels/created3.json',
            'progress_normal': 0,
            'progress_practice': 0,
        }, 
        {
            'name':'Jumper',
            'color': (97, 241, 14),
            'path': './levels/created3.json',
            'progress_normal': 0,
            'progress_practice': 0,
        }, 
    ]
    """ List of OFFICIAL levels parsed from its directory, from which we render pages """
    
    PADDING_Y = 0.1
    PADDING_X = 0.15
    ARROW_BUTTON_PADDING_X_PX = 5 # IN PIXELS
    TOP_BOX_HEIGHT = 0.4
    
    PROGRESS_PADDINGS = 0.35 * (1 - TOP_BOX_HEIGHT - PADDING_Y)
    PROGRESS_GAP = 0.15 * (1 - TOP_BOX_HEIGHT - PADDING_Y)
    PROGRESS_BAR_HEIGHT = ((1 - TOP_BOX_HEIGHT - PADDING_Y) - 2*PROGRESS_PADDINGS - PROGRESS_GAP) / 2
    
    NORMAL_BAR_COLOR = (123, 255, 0)
    PRACTICE_BAR_COLOR = (140, 255, 251)
    
    @classmethod
    def draw_level(c, idx: int):
        
        level_data = c.levels[idx]
        
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

    