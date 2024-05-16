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
    draw('assets/level_menu_title_2.jpeg', Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def draw_publish_button(): 
    draw(f"assets/publish_button.png", pos=Position.Relative(right="calc(30% - 23ch)", bottom="calc(50% - 13ch)"))

class Level_Editor_Menu: 
    def create_menu(): 
          
          draw_menu_background()
          draw_menu_title()
          draw_publish_button() 


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
 

   
    

    


