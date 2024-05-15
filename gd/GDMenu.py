import blessed 
from bottom_menu import draw_square, draw_spike
from img2term.main import draw
from draw_utils import Position
import os

terminal = blessed.Terminal()
os.system('cls')

def draw_gd_icon(width:int, height:int, x: int, y: int, main_color:str, secondary_color:str):

    # Drawing the main body

    draw_square(int(width*1.12), int(height*1.16), int(x*0.88), int(y*0.96), 'light_'+main_color)
    draw_square(width, height, x, y, main_color)
    draw_square(int(width*1.06), int(height*0.08), int(x), int(y*1.92), 'dark_'+main_color)
    draw_square(int(width*0.08), int(height), int(x+width), int(y), 'dark_'+main_color)
    draw_square(int(width*0.08), int(height*0.08), int(x+width), int(y*0.96), 'mid_'+main_color)
    draw_square(int(width*0.08), int(height*0.08), int(x*0.88), int(y*1.92), 'mid_'+main_color)

    # Drawing the eyes

    draw_square(int(width*0.25), int(height*0.3), x+int(width*0.16), y+int(height*0.18), secondary_color)
    draw_square(int(width*0.15), int(height*0.15), x+int(width*0.16), y+int(height*0.18), 'light_'+secondary_color)

    draw_square(int(width*0.25), int(height*0.3), x+int(width*0.6)+1, y+int(height*0.18), secondary_color)
    draw_square(int(width*0.15), int(height*0.15), x+int(width*0.6)+1, y+int(height*0.18), 'light_'+secondary_color)

    # Drawing the mouth

    draw_square(int(width*0.73), 2*int(height*0.18), x+int(width*0.16), y+int(height*0.66), secondary_color)
    draw_square(int(width*0.63), 2*int(height*0.1), x+int(width*0.16), y+int(height*0.66), 'light_'+secondary_color)


def draw_button0(outline=False):

    # If outline is True, draw a white outline around the button

    if outline:

        draw_square(int(terminal.width*0.32), int(terminal.height*0.5), int(terminal.width*0.01), int(terminal.height*0.3), 'white')

    else:
        draw_square(int(terminal.width*0.32), int(terminal.height*0.5), int(terminal.width*0.01), int(terminal.height*0.3), 'black')

    # Drawing the "Customize Icon" button to the screen
        
    draw_square(int(terminal.width*0.295), int(terminal.height*0.46), int(terminal.width*0.02), int(terminal.height*0.32), 'green')

    # Drawing the GD icon on the button

    draw_gd_icon(int(terminal.width*0.21), int(terminal.height*0.34), int(terminal.width*0.06), int(terminal.height*0.38), 'yellow', 'blue2')


def draw_button1(outline=False):

    # If outline is True, draw a white outline around the button

    if outline:

        draw_square(int(terminal.width*0.32), int(terminal.height*0.64), int(terminal.width*0.34), int(terminal.height*0.23), 'white')

    else:
        draw_square(int(terminal.width*0.32), int(terminal.height*0.64), int(terminal.width*0.34), int(terminal.height*0.23), 'black')

    # Drawing the "Play" button to the screen

    draw_square(int(terminal.width*0.3), int(terminal.height*0.6), int(terminal.width*0.35), int(terminal.height*0.24), 'green')

    # Drawing the play icon to the screen

    draw_spike(int(terminal.width*0.05), int(terminal.width*0.43), int(terminal.height*0.35), 'cerulean', True)


def draw_button2(outline=False):

    # If outline is True, draw a white outline around the button

    if outline:

        draw_square(int(terminal.width*0.315), int(terminal.height*0.5), int(terminal.width*0.68), int(terminal.height*0.29), 'white')

    else:
        draw_square(int(terminal.width*0.315), int(terminal.height*0.5), int(terminal.width*0.68), int(terminal.height*0.29), 'black')

    # Drawing the "Level Editor" button to the screen

    draw_square(int(terminal.width*0.29), int(terminal.height*0.46), int(terminal.width*0.69), int(terminal.height*0.32), 'green')

    

    # Yes, I know this part should probably be in a function but it's very late and I'll have to mess with numbers again- problem for future me

    # Drawing the hammer icon onto the screen

    draw_square(int(terminal.width*0.2), int(terminal.height*0.1), int(terminal.width*0.74), int(terminal.height*0.4), 'grey')
    draw_square(int(terminal.width*0.16), int(terminal.height*0.04), int(terminal.width*0.76), int(terminal.height*0.38), 'grey')
    draw_square(int(terminal.width*0.16), int(terminal.height*0.04), int(terminal.width*0.76), int(terminal.height*0.48), 'grey')
    draw_square(int(terminal.width*0.12), int(terminal.height*0.04), int(terminal.width*0.78), int(terminal.height*0.36), 'grey')
    draw_square(int(terminal.width*0.12), int(terminal.height*0.04), int(terminal.width*0.78), int(terminal.height*0.52), 'grey')
    
    draw_square(int(terminal.width*0.04), int(terminal.height*0.2), int(terminal.width*0.82), int(terminal.height*0.54), 'brown')

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
    
    draw(f"assets/main_menu/icon_selector_button{'_outline' if outline else ''}.png",
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
    
    draw(f"assets/main_menu/start_button{'_outline' if outline else ''}.png",
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
    
    draw(f"assets/main_menu/create_button{'_outline' if outline else ''}.png",
        pos=Position.Relative(right="calc(30% - 23ch)", bottom="calc(50% - 13ch)"))