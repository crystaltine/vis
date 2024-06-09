from typing import Literal
from logger import Logger
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from gd_constants import GDConstants
from blessed.keyboard import Keystroke

corner_deco_BL = TextureManager.compile_texture("./assets/menus/corner_deco.png")
corner_deco_BR = TextureManager.reflect_texture(corner_deco_BL, 'horizontal')
corner_deco_TL = TextureManager.reflect_texture(corner_deco_BL, 'vertical')
corner_deco_TR = TextureManager.reflect_texture(corner_deco_BL, 'both')

class CustomLevelsMenu:
    
    curr_frame: CameraFrame | None = None
    
    selected_option = 1
    # 0 = quit, 1 = play, 2 = editor
    
    # Load textures    
    plus_button = TextureManager.compile_texture("./assets/custom_levels_menu/plus_button.png")
    plus_button_outline = TextureManager.compile_texture("./assets/custom_levels_menu/plus_button_outline.png")
    my_levels_button = TextureManager.compile_texture("./assets/custom_levels_menu/my_levels_button.png")
    my_levels_button_outline = TextureManager.compile_texture("./assets/custom_levels_menu/my_levels_button_outline.png")
    online_button = TextureManager.compile_texture("./assets/custom_levels_menu/online_button.png")
    online_button_outline = TextureManager.compile_texture("./assets/custom_levels_menu/online_button_outline.png")
    
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
        new_frame.fill((CustomLevelsMenu.BG_COLOR))

        horiz_center = int(0.5 * new_frame.width)
        title_center = int(CustomLevelsMenu.TITLE_MARGIN_TOP * new_frame.height + TextureManager.font_title.font_height/2)
        
        # draw title text
        new_frame.add_text(horiz_center, title_center, TextureManager.font_title, "Custom Levels", color=CustomLevelsMenu.TITLE_COLOR)
        
        # draw buttons
        middle_button_center_y = int((CustomLevelsMenu.TITLE_MARGIN_TOP + CustomLevelsMenu.TITLE_MARGIN_BOTTOM) * new_frame.height + TextureManager.font_title.font_height + CustomLevelsMenu.MIDDLE_BUTTON_SIZE_PX/2)
        new_frame.add_pixels_centered_at(
            horiz_center,
            middle_button_center_y,
            CustomLevelsMenu.my_levels_button if CustomLevelsMenu.selected_option != 1 else CustomLevelsMenu.my_levels_button_outline
        )
        
        side_button_x_offset = int(CustomLevelsMenu.BUTTON_GAP_X * new_frame.width + CustomLevelsMenu.SIDE_BUTTON_SIZE_PX/2 + CustomLevelsMenu.MIDDLE_BUTTON_SIZE_PX/2)
        new_frame.add_pixels_centered_at(
            horiz_center - side_button_x_offset,
            middle_button_center_y,
            CustomLevelsMenu.plus_button if CustomLevelsMenu.selected_option != 0 else CustomLevelsMenu.plus_button_outline
        )
        
        new_frame.add_pixels_centered_at(
            horiz_center + side_button_x_offset,
            middle_button_center_y,
            CustomLevelsMenu.online_button if CustomLevelsMenu.selected_option != 2 else CustomLevelsMenu.online_button_outline
        )
        
        # add corner decos at the corners
        new_frame.add_pixels_topleft(0, 0, corner_deco_TL)
        new_frame.add_pixels_topleft(new_frame.width - corner_deco_TR.shape[1], 0, corner_deco_TR)
        new_frame.add_pixels_topleft(0, new_frame.height - corner_deco_BL.shape[0], corner_deco_BL)
        new_frame.add_pixels_topleft(new_frame.width - corner_deco_BR.shape[1], new_frame.height - corner_deco_BR.shape[0], corner_deco_BR)
        
        if CustomLevelsMenu.curr_frame is not None:
            new_frame.render(CustomLevelsMenu.curr_frame)
        else: 
            new_frame.render_raw()
        
    def on_key(val: Keystroke) -> Literal['create_new_level', 'open_created_levels', 'open_online_levels'] | None:
        if val.name in ["KEY_LEFT", "KEY_BTAB"]:
            CustomLevelsMenu.selected_option = (CustomLevelsMenu.selected_option - 1) % 3
            CustomLevelsMenu.render()
            
        elif val.name in ["KEY_RIGHT", "KEY_TAB"]:
            CustomLevelsMenu.selected_option = (CustomLevelsMenu.selected_option + 1) % 3
            CustomLevelsMenu.render()
            
        elif val.name == "KEY_ENTER":
            if CustomLevelsMenu.selected_option == 0:
                return 'create_new_level'
            elif CustomLevelsMenu.selected_option == 1:
                return 'open_created_levels'
            elif CustomLevelsMenu.selected_option == 2:
                return 'open_online_levels'

        
        