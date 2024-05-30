import blessed 
#terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position
import os

os.system('clear')

def draw_menu_background(filename:str, terminal): 
    draw(filename, Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def draw_menu_title_online_levels(): 
    left_pos = "calc(50% - 70)"
    top_pos = 4 
    draw('assets/level_editor_menu/level_menu_title_2.jpeg', Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def _draw_search_level_button(outline:bool): 
    draw(f"assets/level_editor_menu/search_button{'_outline' if outline else ''}.png", pos=Position.Relative(left="calc(30% - 13ch)", bottom="calc(50% - 13ch)"))
    #draw(f"assets/main_menu/create_button{'_outline' if outline else ''}.png", pos=Position.Relative(right="calc(50% - 46ch)", bottom="calc(50% - 13ch)"))

def _draw_uploaded_levels_button(outline:bool): 
    draw(f"assets/level_editor_menu/publish_button_main{'_outline' if outline else ''}.png", pos=Position.Relative(right="calc(50% - 46ch)", bottom="calc(50% - 13ch)"))

def draw_all_buttons_online(outline_index=0): 
    
    _draw_search_level_button(outline_index==0)
    _draw_uploaded_levels_button(outline_index==1)
  
    
def init_online_levels_page(terminal): 
          
    draw_menu_background('assets/level_editor_menu/level_editor_menu.png', terminal)
    draw_menu_title_online_levels()
    draw_all_buttons_online(0)




