import blessed 
#terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position
import os

os.system('clear')

def draw_menu_background(filename:str, terminal): 
    draw(filename, Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def draw_menu_title_level_editor(): 
    left_pos = "calc(50% - 70)"
    top_pos = 4 
    draw('gd/assets/level_editor_menu/level_menu_title_2.jpeg', Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def _draw_create_level_button(outline:bool): 
    draw(f"assets/main_menu/create_button{'_outline' if outline else ''}.png", pos=Position.Relative(left="calc(30% - 13ch)", bottom="calc(50% - 13ch)"))
    #draw(f"assets/main_menu/create_button{'_outline' if outline else ''}.png", pos=Position.Relative(right="calc(50% - 46ch)", bottom="calc(50% - 13ch)"))

def _draw_search_button(outline:bool): 
    draw(f"assets/level_editor_menu/search_button{'_outline' if outline else ''}.png", pos=Position.Relative(right="calc(30% - 45ch)", bottom="calc(50% - 13ch)"))

def _draw_created_levels_button(outline:bool):

    draw(f"assets/level_editor_menu/my_levels_button{'_outline' if outline else ''}.png", pos=Position.Relative(left="calc(50% - 14ch)", bottom="calc(50% - 13ch)")) 
    #draw(f"assets/level_editor_menu/my_levels_button{'_outline' if outline else ''}.png", pos=Position.Relative(left="calc(30% - 13ch)", bottom="calc(50% - 13ch)")) 

def _draw_start_button(outline:bool): 
     draw(f"gd/assets/level_editor_menu/start_button_smaller{'_outline' if outline else ''}.png", pos=Position.Relative(left="calc(50% - 14ch)", bottom="calc(50% - 13ch)"))

def _draw_online_levels_button(outline:bool):
    draw(f"assets/level_editor_menu/search_button{'_outline' if outline else ''}.png", pos=Position.Relative(right="calc(50% - 46ch)", bottom="calc(50% - 13ch)"))
    #draw(f"assets/level_editor_menu/search_button{'_outline' if outline else ''}.png", pos=Position.Relative(right="calc(30% - 45ch)", bottom="calc(50% - 13ch)"))

def draw_all_buttons(outline_index=0): 
    
    _draw_create_level_button(outline_index==0)
    _draw_created_levels_button(outline_index==1)
    _draw_online_levels_button(outline_index==2)
    
def init_level_editor_page(terminal): 
          
          draw_menu_background('assets/level_editor_menu/level_editor_menu.png', terminal)
          draw_menu_title_level_editor()
          draw_all_buttons(0)




