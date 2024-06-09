from typing import Literal
from logger import Logger
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from gd_constants import GDConstants
from blessed.keyboard import Keystroke

class MainMenu:
    
    curr_frame: CameraFrame | None = None
    
    selected_option = 1
    # 0 = quit, 1 = play, 2 = editor
    
    # Load textures    
    start_button = TextureManager.compile_texture("./assets/main_menu/start_button.png")
    start_button_outline = TextureManager.compile_texture("./assets/main_menu/start_button_outline.png")
    quit_button = TextureManager.compile_texture("./assets/main_menu/quit_button.png")
    quit_button_outline = TextureManager.compile_texture("./assets/main_menu/quit_button_outline.png")
    editor_button = TextureManager.compile_texture("./assets/main_menu/editor_button.png")
    editor_button_outline = TextureManager.compile_texture("./assets/main_menu/editor_button_outline.png")
    
    # style constants
    BG_COLOR = (63, 72, 204)
    GROUND_COLOR = (29, 37, 143)
    TITLE_COLOR = (129, 255, 90)
    GROUND_MARGIN_TOP = 0.7 # ground at 70% of the screen
    TITLE_MARGIN_Y = 0.15
    BUTTON_GAP_X = 0.08
    SIDE_BUTTON_SIZE_PX = 28 # px
    MIDDLE_BUTTON_SIZE_PX = 36 # px
    
    def render():
        new_frame = CameraFrame()
        new_frame.fill((MainMenu.BG_COLOR))
        
        # add rectangle for ground
        new_frame.add_rect(
            MainMenu.GROUND_COLOR,
            0, int(MainMenu.GROUND_MARGIN_TOP * new_frame.height),
            new_frame.width, (new_frame.height - int(MainMenu.GROUND_MARGIN_TOP * new_frame.height))
        )
        
        horiz_center = int(0.5 * new_frame.width)
        title_center = int(MainMenu.TITLE_MARGIN_Y * new_frame.height + TextureManager.font_title.font_height/2)
        
        # draw title text
        new_frame.add_text(horiz_center, title_center, TextureManager.font_title, "Geometry Dash", color=MainMenu.TITLE_COLOR)
        
        # draw buttons
        middle_button_center_y = int(MainMenu.TITLE_MARGIN_Y*2 * new_frame.height + TextureManager.font_title.font_height + MainMenu.MIDDLE_BUTTON_SIZE_PX/2)
        new_frame.add_pixels_centered_at(
            horiz_center,
            middle_button_center_y,
            MainMenu.start_button if MainMenu.selected_option != 1 else MainMenu.start_button_outline
        )
        
        side_button_x_offset = int(MainMenu.BUTTON_GAP_X * new_frame.width + MainMenu.SIDE_BUTTON_SIZE_PX/2 + MainMenu.MIDDLE_BUTTON_SIZE_PX/2)
        new_frame.add_pixels_centered_at(
            horiz_center - side_button_x_offset,
            middle_button_center_y,
            MainMenu.quit_button if MainMenu.selected_option != 0 else MainMenu.quit_button_outline
        )
        
        new_frame.add_pixels_centered_at(
            horiz_center + side_button_x_offset,
            middle_button_center_y,
            MainMenu.editor_button if MainMenu.selected_option != 2 else MainMenu.editor_button_outline
        )
        
        if MainMenu.curr_frame is not None:
            new_frame.render(MainMenu.curr_frame)
        else: 
            new_frame.render_raw()
        
    def on_key(val: Keystroke) -> Literal['quit', 'play', 'editor'] | None:
        if val.name in ["KEY_LEFT", "KEY_BTAB"]:
            MainMenu.selected_option = (MainMenu.selected_option - 1) % 3
            MainMenu.render()
            
        elif val.name in ["KEY_RIGHT", "KEY_TAB"]:
            MainMenu.selected_option = (MainMenu.selected_option + 1) % 3
            MainMenu.render()
            
        elif val.name == "KEY_ENTER":
            if MainMenu.selected_option == 0:
                return 'quit'
            elif MainMenu.selected_option == 1:
                return 'play'
            elif MainMenu.selected_option == 2:
                return 'editor'

        
        