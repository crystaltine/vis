import blessed 
terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position 
import os

os.system('clear') 

def menu_bg(filename:str): 
    draw(filename, Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def menu_title(filename:str): 
    left_pos = "calc(50% - 70)"
    top_pos = 4 
    draw(filename, Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def loading_text(filename:str): 
    left_pos = "calc(50% - 100)"
    top_pos = 20
    draw(filename, Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def create_menu(): 
          
          menu_bg('assets/menu_bg.png')
          menu_title('assets/main_menu_title_2_better.png')
          loading_text('assets/loading.png')

          with terminal.hidden_cursor():

            while True:
                with terminal.cbreak():
                    val = terminal.inkey(timeout=1)
                    if val == 'q':
                        os.system('clear')
                        break 

                    elif val.name == 'KEY_ENTER': 
                        menu_bg('assets/red_bg.png')

                    elif val.name == 'KEY_ESCAPE':
                        menu_bg('assets/menu_bg.png')
                        menu_title('assets/main_menu_title_2_better.png')
                        loading_text('assets/loading.png')

#function call 
create_menu()