import blessed 
terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position
import os

os.system('clear')
current_button_index=1 

def draw_menu_background(): 
    draw('assets/level_editor_menu/level_editor_menu.png', Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def draw_menu_title(): 
    left_pos = "calc(50% - 70)"
    top_pos = 4 
    draw('assets/level_editor_menu/level_menu_title_2.jpeg', Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def draw_publish_button(outline:bool): 
    draw(f"assets/level_editor_menu/publish_button_main{'_outline' if outline else ''}.png", pos=Position.Relative(left="calc(30% - 44.8ch)", bottom="calc(50% - 13ch)"))

def draw_create_button(outline:bool): 
    draw(f"assets/main_menu/create_button{'_outline' if outline else ''}.png", pos=Position.Relative(right="calc(50% - 46ch)", bottom="calc(50% - 13ch)"))

def draw_search_button(outline:bool): 
    draw(f"assets/level_editor_menu/search_button{'_outline' if outline else ''}.png", pos=Position.Relative(right="calc(30% - 45ch)", bottom="calc(50% - 13ch)"))

def draw_my_levels_button(outline:bool): 
    draw(f"assets/level_editor_menu/my_levels_button{'_outline' if outline else ''}.png", pos=Position.Relative(left="calc(30% - 13ch)", bottom="calc(50% - 13ch)")) 

def _draw_start_button(outline:bool): 
     draw(f"assets/level_editor_menu/start_button_smaller{'_outline' if outline else ''}.png", pos=Position.Relative(left="calc(50% - 14ch)", bottom="calc(50% - 13ch)"))

def draw_all_buttons(number): 
    if number == 1: 
        draw_publish_button(True)
        draw_create_button(False)
        draw_search_button(False)
        draw_my_levels_button(False) 
        _draw_start_button(False)
    elif number == 2: 
        draw_create_button(True)
        draw_publish_button(False)
        draw_search_button(False)
        draw_my_levels_button(False) 
        _draw_start_button(False)
    elif number == 3: 
        draw_search_button(True)
        draw_publish_button(False)
        draw_create_button(False)
        draw_my_levels_button(False) 
        _draw_start_button(False)
    elif number == 4: 
        draw_my_levels_button(True) 
        draw_search_button(False)
        draw_publish_button(False)
        draw_create_button(False)
        _draw_start_button(False)
    elif number == 5: 
        _draw_start_button(True)
        draw_my_levels_button(False) 
        draw_search_button(False)
        draw_publish_button(False)
        draw_create_button(False)
    
def create_menu(): 
          
          draw_menu_background()
          draw_menu_title()
          draw_all_buttons(1) 

          with terminal.hidden_cursor():

            while True:
                with terminal.cbreak():
                    val = terminal.inkey(timeout=1)
                    if val == "q":
                        os.system('clear')
                        break 
                    else: 
                        handle_main_page_movement(val)

def handle_main_page_movement(val):
        global current_button_index

        changed=False

        if val.name=='KEY_LEFT':
            changed=True
            current_button_index-=1
            if current_button_index<0:
                current_button_index=2

        if val.name=='KEY_RIGHT':
            changed=True
            current_button_index+=1
            if current_button_index>2:
                current_button_index=0

        if changed:
            draw_all_buttons(current_button_index)

create_menu()
