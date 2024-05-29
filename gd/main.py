import logging
import blessed
from draw_utils import Position, draw_rect
import traceback
from GDMenu import draw_main_menu_buttons
from level_selector import *
import os 
from img2term.main import draw
# from run_gd import run_level
from logger import Logger
from game import Game
from parse import parse_level
from copy import deepcopy
from main_page import *
import sys

current_module = sys.modules[__name__]
terminal = blessed.Terminal()

main_current_index=1
level_select_index=0

# currentgame stores the current attempt of a certain level within the game
currentgame = None
# the number of attempts currently tried within a certain level in the game
attempt = 0
pages={'main':['character_select', 'level_select', 'level_editor'], 'character_select':[], 'level_select':['play_level'], 'level_editor':[], 'play_level':[]}
current_page={'previous_page':'main', 'current_screen':'main', 'current_page':0}

def draw_menu_bg():
    """ This is a very crude function im writing at 5am ill make it better later """
    draw('assets/menu_bg_1.png', Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')



def main():

    global currentgame

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
                
                # handles exit code from level selector or exiting from pause menu within the level
                if ((val.name=="KEY_ESCAPE" and current_page['current_screen']!='main' and current_page['current_screen']!='play_level') or (currentgame != None and current_page['current_screen']=='play_level' and currentgame.exiting)) :
                    # unsets the current game as the attempt is now complete
                    render_new_page(current_page['previous_page'])

                # handles resetting the game (occurs after each death)
                if ((currentgame != None and current_page['current_screen']=='play_level' and currentgame.reseting)):
                    practice_mode = False
                    checkpoints = []
                    # if the game was in practice mode, saves the checkpoints that were stored in the previous attempt
                    if currentgame.practice_mode:
                        practice_mode = True
                        if currentgame.checkpoints:
                            checkpoints = deepcopy(currentgame.checkpoints)
                    currentgame = None
                    # runs the level with the necessary paramaters based on if it is in practice mode or not
                    run_level(levels[level_select_index]['path'], practice_mode, checkpoints)

                # The call_handle_page_function will call the corresponding function to handle all the specific key bindings for each page

                call_handle_page_function(val)

def render_new_page(new_page:str):

    global current_page

    # Here, the previous_page to the new_page is getting updated, along with the current_screen and current_page
    Logger.log(f"Switching from {current_page['current_screen']} to {new_page}")
    
    current_page['previous_page']=pull_prev_page(new_page)
    current_page['current_screen']=new_page
    current_page['current_page']=0

    # Play_level is the only page that doesn't follow the generic "init_[page]" function structure as the other pages

    if new_page=='play_level':
        run_level(levels[level_select_index]['path'])
    else:
        init_function=getattr(current_module, 'init_'+new_page+'_page')
        init_function(terminal)

    # draw all three buttons, select middle one by default
    draw_main_menu_buttons(1)
 
def init_level_selector():
    global attempt

    # draw fullscreen bg
    draw_rect("#000000", Position.Relative(0, 0, 0, 0))

def pull_prev_page(new_page:str):
    prev_page='main'
    for screen in pages:
        if new_page in pages[screen]:
            prev_page=screen
    return prev_page


def call_handle_page_function(val):
    if current_page['current_screen']!='play_level':
        
        handle_function=getattr(current_module, 'handle_'+current_page['current_screen']+'_page')
        handle_function(val)

    level_info=levels[0]
    # resets the attempt number when returning to the level selector screen
    attempt = 0
    draw_level(level_info['level_name'], level_info['level_description'], int(terminal.width*0.8), int(terminal.height*0.6), 
                   int(terminal.width*0.1), int(terminal.height*0.3), level_info['color1'], level_info['color2'])

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
        
        run_level(levels[level_select_index]['path'])

    # If a button has been pressed, reset the level, and regenerate the new level onto the screen

    if changed:

        level_info=levels[level_select_index]
        reset_level()
        draw_level(level_info['level_name'], level_info['level_description'], int(terminal.width*0.8), int(terminal.height*0.6), 
                   int(terminal.width*0.1), int(terminal.height*0.3), level_info['color1'], level_info['color2'])

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
        for row in leveldata:
            Logger.log(f"Level row types: {[type(row_obj) for row_obj in row]}")

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
        Logger.log(f"Error in CharacterSelect.render(): {e}")
        Logger.log(f"Traceback: {traceback.format_exc()}")
        print(f"\x1b[31m{traceback.format_exc()}\x1b[0m")
        
    Logger.write()
        
