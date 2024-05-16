import blessed 
terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position
from GDMenu import _draw_start_button
import os

os.system('clear')

def draw_menu_background(): 
    draw('assets/level_editor_menu.png', Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def draw_menu_title(): 
    left_pos = "calc(50% - 70)"
    top_pos = 4 
    draw('assets/level_menu_title_2.jpeg', Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

class Level_Editor_Menu: 
    def create_menu(): 
          
          draw_menu_background()
          draw_menu_title()
          _draw_start_button() 


          with terminal.hidden_cursor():

            while True:

                with terminal.cbreak():
                    
                    val = terminal.inkey(timeout=1)

                    # Quitting game if q is hit

                    if val == "q":
                        os.system('cls')
                        break        
#function calls 
    create_menu()
 

   
    

    


