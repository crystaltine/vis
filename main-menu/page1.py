import blessed 
terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position 
import os

os.system('clear') 

def menu_bg(filename:str): 
    draw(filename, Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def menu_title(text:str, left_pos, top_pos): 
    draw(text, Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')


def create_menu(): 
          
          menu_bg('assets/menu_bg.png')
          menu_title('assets/main_menu_title_2_better.png', "calc(50%-70)", 4)
          menu_title('assets/loading.png', "calc(50%-50)", 1)

          with terminal.hidden_cursor():

            while True:
                with terminal.cbreak():
                    val = terminal.inkey(timeout=1)
                    if val == "q":
                        os.system('clear')
                        break 
create_menu()