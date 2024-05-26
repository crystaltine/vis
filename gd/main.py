import logging
import blessed
from draw_utils import Position, draw_rect
import traceback
from GDMenu import draw_main_menu_buttons
from level_selector import *
import os 
from img2term.main import draw
from run_gd import run_level
from logger import Logger
from main_page import *
import sys

current_module = sys.modules[__name__]
terminal = blessed.Terminal()

main_current_index=1
level_select_index=0

pages={'main':['character_select', 'level_select', 'level_editor'], 'character_select':[], 'level_select':['play_level'], 'level_editor':[],
        'play_level':[]}

current_page={'previous_page':'main', 'current_screen':'main', 'current_page':0}

def main():

    init_main_page(terminal)

    with terminal.hidden_cursor():

        while True:

            # The only page that needs text on the top of the screen is the level selector

            if current_page['current_screen']!='level_select':
                draw_text('', 0, 0)
            
            else:
                draw_text('LEVEL_SELECTOR', int((terminal.width-len('LEVEL_SELECTOR'))*0.5), int(terminal.height*0.1))

            with terminal.cbreak():
                
                val = terminal.inkey(timeout=1)

                # Quitting game if q is hit

                if val == "q":
                    os.system('cls')
                    break
                
                if val.name=="KEY_ESCAPE" and current_page['current_screen']!='main':
                    
                    render_new_page(current_page['previous_page'])

                # The call_handle_page_function will call the corresponding function to handle all the specific key bindings for each page

                call_handle_page_function(val)

def render_new_page(new_page:str):

    global current_page

    # Here, the previous_page to the new_page is getting updated, along with the current_screen and current_page

    current_page['previous_page']=pull_prev_page(new_page)
    current_page['current_screen']=new_page
    current_page['current_page']=0

    # Play_level is the only page that doesn't follow the generic "init_[page]" function structure as the other pages

    if new_page=='play_level':
        run_level(levels[level_select_index]['path'])
    else:
        init_function=getattr(current_module, 'init_'+new_page+'_page')
        init_function(terminal)


def pull_prev_page(new_page:str):
    prev_page='main'
    for screen in pages:
        if new_page in pages[screen]:
            prev_page=screen
    return prev_page


def call_handle_page_function(val):
    
    handle_function=getattr(current_module, 'handle_'+current_page['current_screen']+'_page')
    handle_function(val)


def handle_main_page(val):

    global main_current_index
    

    changed=False

    # Arrow keys to select a different button
    
    if val.name=='KEY_LEFT':
        
        changed=True
        
        main_current_index-=1

        if main_current_index<0:
            main_current_index=2
        
    if val.name=='KEY_RIGHT':
        
        changed=True
        main_current_index+=1
        if main_current_index>2:
            main_current_index=0

    # Opening the level selector if space is selected

    if val.name=='KEY_ENTER' and main_current_index==1:
        
        render_new_page('level_select')
       
    # If a button has been pressed, we rerender the new button and the previous button to get rid of/add in the white outline

    if changed:
        draw_main_menu_buttons(main_current_index)


def handle_level_select_page(val):

    # Change level_select_index if arrow keys pressed

    global level_select_index
  
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
        render_new_page('play_level')
        
    # If a button has been pressed, reset the level, and regenerate the new level onto the screen

    if changed:

        level_info=levels[level_select_index]
        reset_level()
        draw_level(level_info['level_name'], level_info['level_description'], int(terminal.width*0.8), int(terminal.height*0.6), 
                   int(terminal.width*0.1), int(terminal.height*0.3), level_info['color1'], level_info['color2'])

if __name__ == "__main__":
    # testing
    try:
        main()
    except Exception as e:
        Logger.log(f"Error in CharacterSelect.render(): {e}")
        Logger.log(f"Traceback: {traceback.format_exc()}")
        print(f"\x1b[31m{traceback.format_exc()}\x1b[0m")
        
    Logger.write()
        
