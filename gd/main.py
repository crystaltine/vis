import blessed
import GDMenu
from GDMenu import draw_button0, draw_button1, draw_button2, draw_text, draw_square
import os 
from img2term.main import draw
from logger import Logger

terminal = blessed.Terminal()

def draw_menu_bg():
    """ This is a very crude function im writing at 5am ill make it better later """
    draw('menu_images/menu_bg_1.png', (0, 0), (terminal.width, terminal.height*2), 'scale')

def draw_menu_title():
    """ Attempts to draw the GEOMETRY DASH title in the center-top of the screen. it's 141 pixels wide, so requires fullscreen.
    Who knows what horrors will happen if the term isn't that wide...
    """
    left_pos = int(terminal.width/2) - 70
    top_pos = 2 # arbitrary value
    draw('menu_images/menu_title_1_editable.png', (left_pos, top_pos), (None, None), 'crop')
    
def main():

    # Reset scren to black

    #draw_square(terminal.width, terminal.height, 0, 0, 'black')
    draw_menu_bg()
    draw_menu_title()

    # Drawing 3 buttons onto screen with middle button selected by default

    draw_button0()
    draw_button1(True)
    draw_button2()

    current_index=1
    
    with terminal.hidden_cursor():

        while True:

            with terminal.cbreak():
                changed=False
                old_index=0

                val = terminal.inkey(timeout=1)

                # Quitting game if q is hit

                if val == "q":
                    #Logger.write()
                    break

                # Arrow keys to select a different button

                if val.name=='KEY_LEFT':
                    old_index=current_index
                    changed=True
                    
                    current_index-=1
                    if current_index<0:
                        current_index=2
                    
                if val.name=='KEY_RIGHT':
                    old_index=current_index
                    changed=True
                    current_index+=1
                    if current_index>2:
                        current_index=0

                # Running test gd file if space is selected

                if val==' ' and current_index==1:
                    os.system('python run_gd.py')


                # If a button has been pressed, we rerender the new button and the previous button to get rid of/add in the white outline

                if changed:
                    
                    # Rerendering the new buttons

                    deselect_prev_button = getattr(GDMenu, 'draw_button'+str(old_index))
                    deselect_prev_button()

                    select_new_button = getattr(GDMenu, 'draw_button'+str(current_index))
                    select_new_button(True)

main()
