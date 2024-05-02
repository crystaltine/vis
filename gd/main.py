import blessed
import GDMenu
from GDMenu import draw_button0, draw_button1, draw_button2, draw_text, draw_square
from level_selector import *
import os 
from img2term.main import draw
from run_gd import run_level

terminal = blessed.Terminal()

main_current_index=1
level_select_index=0
pages=['main', 'LEVEL SELECTOR', 'level']
current_page_index=0

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

    global current_page_index

    init_main_page()

    with terminal.hidden_cursor():

        while True:

            # The only page that needs text on the top of the screen is the level selector

            if pages[current_page_index]!='LEVEL SELECTOR':
                draw_text('', int((terminal.width-len(pages[current_page_index]))*0.5), int(terminal.height*0.1))
            
            else:
                draw_text(pages[current_page_index], int((terminal.width-len(pages[current_page_index]))*0.5), int(terminal.height*0.1))

            with terminal.cbreak():
                
                val = terminal.inkey(timeout=1)

                # Quitting game if q is hit

                if val == "q":
                    os.system('cls')
                    break
                
                if current_page_index>0 and val.name=="KEY_ESCAPE":
                    current_page_index-=1
                    render_new_page()

                call_handle_page_function(val)

def render_new_page():

    if pages[current_page_index]=='main':
        init_main_page()
    
    elif pages[current_page_index]=='LEVEL SELECTOR':
        init_level_selector()

def call_handle_page_function(val):

    if pages[current_page_index]=='main':
        handle_main_page(val)
    
    elif pages[current_page_index]=='LEVEL SELECTOR':
        handle_level_select_page(val)

def init_main_page():

    draw_menu_bg()
    draw_menu_title()

    # Drawing 3 buttons onto screen with middle button selected by default

    draw_button0()
    draw_button1(True)
    draw_button2()

def init_level_selector():

    draw_square(terminal.width, terminal.height, 0, 0, 'black')

    selector_text='Select a level by navigating with the arrow keys and hitting enter once you have chosen a level'
    draw_text(selector_text, int(terminal.width*0.23), int(terminal.height*0.2))

    # Drawing the two arrows on each side of the level

    draw_spike(int(terminal.width*0.025), int(terminal.width*0.95), int(terminal.height*0.5), 'white', True)
    draw_spike(int(terminal.width*0.025), int(terminal.width*0.03), int(terminal.height*0.5), 'white', False, True)

    level_info=levels[0]
    draw_level(level_info['level_name'], level_info['level_description'], int(terminal.width*0.8), int(terminal.height*0.6), 
                   int(terminal.width*0.1), int(terminal.height*0.3), level_info['color1'], level_info['color2'])

def handle_main_page(val):

    global main_current_index
    global current_page_index

    changed=False
    old_index=0

    # Arrow keys to select a different button
    
    if val.name=='KEY_LEFT':
        old_index=main_current_index
        changed=True
        
        main_current_index-=1

        if main_current_index<0:
            main_current_index=2
        
    if val.name=='KEY_RIGHT':
        old_index=main_current_index
        changed=True
        main_current_index+=1
        if main_current_index>2:
            main_current_index=0

    # Opening the level selector if space is selected

    if val.name=='KEY_ENTER' and main_current_index==1:
        
        current_page_index=1

        init_level_selector()
       
    # If a button has been pressed, we rerender the new button and the previous button to get rid of/add in the white outline

    if changed:
        
        # Rerendering the new buttons

        deselect_prev_button = getattr(GDMenu, 'draw_button'+str(old_index))
        deselect_prev_button()

        select_new_button = getattr(GDMenu, 'draw_button'+str(main_current_index))
        select_new_button(True)


def handle_level_select_page(val):

    # Change level_select_index if arrow keys pressed

    global level_select_index
    global current_page_index

    changed=False
    if val.name=='KEY_LEFT':
        
        changed=True
        
        level_select_index-=1
        if level_select_index<0:
            level_select_index=len(levels)-1
        
    if val.name=='KEY_RIGHT':
        changed=True
        level_select_index+=1
        if level_select_index>len(levels)-1:
            level_select_index=0
    
    # Running test gd file if space is selected

    if val.name=='KEY_ENTER':
        current_page_index=2
        
        run_level(levels[level_select_index]['path'])

    # If a button has been pressed, reset the level, and regenerate the new level onto the screen

    if changed:

        level_info=levels[level_select_index]
        reset_level()
        draw_level(level_info['level_name'], level_info['level_description'], int(terminal.width*0.8), int(terminal.height*0.6), 
                   int(terminal.width*0.1), int(terminal.height*0.3), level_info['color1'], level_info['color2'])

main()
