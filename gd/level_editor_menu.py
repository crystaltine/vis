import blessed 
terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position
import os

os.system('clear')

def draw_menu_background(): 
    draw('assets/level_editor_menu.png', Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def draw_menu_title(): 
    left_pos = "calc(50% - 70)"
    top_pos = 4 
    draw('assets/level_editor_menu/level_menu_title_2.jpeg', Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def draw_publish_button(): 
    draw(f"assets/level_editor_menu/publish_button_main.png", pos=Position.Relative(right="calc(30% - 23ch)", bottom="calc(50% - 13ch)"))

def draw_create_button(): 
      draw(f"assets/main_menu/create_button.png", pos=Position.Relative(left="calc(50% - 18ch)", bottom="calc(50% - 15ch)"))

def draw_search_button(): 
    return None

def draw_my_levels_button(): 
    return None 

def draw_all_buttons(): 
    draw_publish_button()
    draw_create_button()
    draw_search_button()
    draw_my_levels_button() 

class Level_Editor_Menu: 
    def create_menu(): 
          
          draw_menu_background()
          draw_menu_title()
          draw_all_buttons()

          with terminal.hidden_cursor():

            while True:
                with terminal.cbreak():
                    val = terminal.inkey(timeout=1)
                    if val == "q":
                        os.system('cls')
                        break        
#function calls 
    create_menu()
 

   
    

    


