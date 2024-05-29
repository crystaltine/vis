import logging
import random
import blessed
from draw_utils import Position, draw_rect
import traceback
from GDMenu import draw_main_menu_buttons
from level_selector import *
from level_editor_menu import *
from online_levels import *
import os 
from img2term.main import draw
from run_level_editor import *
# from run_gd import run_level
from logger import Logger
from main_page import *
import sys
from game import Game
from parse_level import parse_level
from copy import deepcopy
from created_levels import *

current_module = sys.modules[__name__]
terminal = blessed.Terminal()

level_select_index=0
created_levels_index=0
currentgame = None
attempt = 0

pages={'main':['character_select', 'level_select', 'level_editor'], 'character_select':[], 'level_select':['play_level'], 
       'level_editor':['create_level', 'created_levels', 'online_levels'], 'play_level':[], 'create_level':[], 'created_levels':[], 
       'online_levels':['search_levels', 'upload_levels'], 'search_levels':[], 'upload_levels':[]}

current_page={'previous_page':'main', 'current_screen':'main', 'current_page':1}

def main():

    init_main_page(terminal)

    with terminal.hidden_cursor():

        while True:

            # The only page that needs text on the top of the screen is the level selector

            if current_page['current_screen']=='level_select':
                draw_text('LEVEL SELECTOR', int((terminal.width-len('LEVEL SELECTOR'))*0.5), int(terminal.height*0.1))
            elif current_page['current_screen']=='created_levels':
                draw_text('CREATED LEVELS', int((terminal.width-len('Created Levels'))*0.5), int(terminal.height*0.1))
            else:
                draw_text('', 0, 0)

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

    if new_page=='main':
        current_page['current_page']=1

    # Play_level is the only page that doesn't follow the generic "init_[page]" function structure as the other pages

    if new_page=='play_level':
        run_level(levels[level_select_index]['path'])
    elif new_page=='create_level':
        run_editor()
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

    if current_page['current_screen']=='level_select' or current_page['current_screen']=='created_levels':
        handle_function=getattr(current_module, 'handle_'+current_page['current_screen']+'_page')
        handle_function(val)

    elif current_page['current_screen']!='play_level':
        handle_generic_page(val)
        

def handle_generic_page(val):
    global current_page
    global levels

    changed=False

    # Arrow keys to select a different button
    
    if val.name=='KEY_LEFT':
        
        changed=True
        
        current_page['current_page']-=1

        if current_page['current_page']<0:
            current_page['current_page']=len(pages[current_page['current_screen']])-1
        
    if val.name=='KEY_RIGHT':
        
        changed=True
        current_page['current_page']+=1
        if current_page['current_page']>len(pages[current_page['current_screen']])-1:
            current_page['current_page']=0

    # Opening the level selector if space is selected

    if val.name=='KEY_ENTER':
        
        render_new_page(pages[current_page['current_screen']][current_page['current_page']])
    
    if changed:
        if current_page['current_screen']=='main':
            draw_main_menu_buttons(current_page['current_page'])
        elif current_page['current_screen']=='level_editor':
            draw_all_buttons(current_page['current_page'])
        elif current_page['current_screen']=='online_levels':
            draw_all_buttons_online(current_page['current_page'])

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
        
def handle_created_levels_page(val):

    # Change level_select_index if arrow keys pressed

    global created_levels_index
  
    changed=False
    
    if val.name=='KEY_LEFT':
        
        changed=True
        
        created_levels_index-=1
        if created_levels_index<0:
            created_levels_index=len(levels)-1
        
    if val.name=='KEY_RIGHT':
        changed=True
        created_levels_index+=1
        if created_levels_index>len(levels)-1:
           created_levels_index=0
    
    # Running test gd file if space is selected

    if val.name=='KEY_ENTER':
        render_new_page('play_level')
        
    # If a button has been pressed, reset the level, and regenerate the new level onto the screen

    if changed:

        level_info=level_file_names[created_levels_index]
        reset_level()
        color=random.choice(colors)
        draw_created_level(level_info[level_info.index('\\')+1:level_info.index('.level')], int(terminal.width*0.8), int(terminal.height*0.6), 
                   int(terminal.width*0.1), int(terminal.height*0.3), color[0], color[1])

def run_level(path: str, practice_mode: bool = False, checkpoints: list[tuple[float, float]] = None) -> None:
    """
    Runs the specified level from the given path utilizing the given checkpoints (if any).
    Args:
        path (str): The path to the level file to be run. (e.g. "levels/level1.txt")
        practice_mode (bool): If True, the level will be run in practice mode. Defaults to False.
        checkpoints (list[tuple[float, float]]): A list of checkpoint coordinates (for practice mode), each checkpoint is a tuple of (x, y) positions. Defaults to None.
    """
    global currentgame
    global attempt

    leveldata = path
    if isinstance(leveldata, str):
        leveldata = parse_level(leveldata)

    currentgame = Game(leveldata)
    # increments the attempt number
    attempt += 1
    currentgame.attempt = attempt

    # if the level is in practice mode, then it sets it as so
    if practice_mode:
        currentgame.practice_mode = True
        # if the level has existing checkpoints, it adds them into the current game
        # additionally, it sets the most recent checkpoint, and the player position there
        # this is so that in practice mode the player will respawn at the most recent checkpoint
        if checkpoints:
            currentgame.checkpoints = checkpoints
            currentgame.last_checkpoint = checkpoints[-1]
            currentgame.player.pos = [currentgame.last_checkpoint[0], currentgame.last_checkpoint[1]]

    currentgame.start_level()

if __name__ == "__main__":
    # testing
    try:
        main()
    except Exception as e:
        Logger.log(f"Error in main.py: {e}")
        Logger.log(f"Traceback: {traceback.format_exc()}")
        print(f"\x1b[31m{traceback.format_exc()}\x1b[0m")
        
    Logger.write()
        
