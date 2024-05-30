from bottom_menu import *
from draw_utils import draw_rect, Position, convert_to_chars
from img2term.main import draw
import os

os.system('clear')

def draw_main_menu_buttons(outlined_idx: int = 1) -> None:
    """
    Main function to draw all three main menu buttons.
    Outlined index refers to which button should be outlined (selected/hovered).
    0 is the left button (icon select)
    1 is middle button (start/main levels)
    2 is right button (level editor/search)
    """
    
    _draw_icon_selector_button(outlined_idx == 0)
    _draw_start_button(outlined_idx == 1)
    _draw_create_button(outlined_idx == 2)

def _draw_icon_selector_button(outline: bool = False):
    """
    Draw button that opens the icon selector on the main menu. (left)
    Filenames for button textures:
    - assets/main_menu/icon_selector_button.png
    - assets/main_menu/icon_selector_button_outline.png
    
    This button is 28ch wide and 14 ch tall.
    
    ## important:
    see gd/assets/main_menu/main_menu_layout_calcs.png for the calculations/numbers used in this method.
    """
    
    draw(f"gd/assets/main_menu/icon_selector_button{'_outline' if outline else ''}.png",
        pos=Position.Relative(left="calc(30% - 23ch)", bottom="calc(50% - 13ch)"))
    
def _draw_start_button(outline: bool = False):
    """
    Draw button that opens the main level selector on the main menu. (middle)
    Filenames for button textures:
    - assets/main_menu/start_button.png
    - assets/main_menu/start_button_outline.png
    
    This button is 36ch wide and 18ch tall.
    
    ## important:
    see gd/assets/main_menu/main_menu_layout_calcs.png for the calculations/numbers used in this method.
    """
    
    draw(f"gd/assets/main_menu/start_button{'_outline' if outline else ''}.png",
        pos=Position.Relative(left="calc(50% - 18ch)", bottom="calc(50% - 15ch)"))
    
def _draw_create_button(outline: bool = False):
    """
    Draw button that opens the level editor/search on the main menu. (right)
    Filenames for button textures:
    - assets/main_menu/create_button.png
    - assets/main_menu/create_button_outline.png
    
    This button is 28ch wide and 14ch tall.
    
    ## important:
    see gd/assets/main_menu/main_menu_layout_calcs.png for the calculations/numbers used in this method.
    """
    
    draw(f"gd/assets/main_menu/create_button{'_outline' if outline else ''}.png",
        pos=Position.Relative(right="calc(30% - 23ch)", bottom="calc(50% - 13ch)"))

def draw_menu_bg(terminal):
    """ This is a very crude function im writing at 5am ill make it better later """
    draw('gd/assets/menu_bg_1.png', Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def draw_menu_title():
    """ Attempts to draw the GEOMETRY DASH title in the center-top of the screen. it's 141 pixels wide, so requires fullscreen.
    Who knows what horrors will happen if the term isn't that wide...
    """
    
    # important: title img is 141ch x 7ch
    
    left_pos = "calc(50% - 70)"
    top_pos = 4 # arbitrary value
    draw('gd/assets/menu_title_1_editable.png', Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def init_main_page(terminal):

    draw_menu_bg(terminal)
    draw_menu_title()

    # draw all three buttons, select middle one by default
    draw_main_menu_buttons(1)