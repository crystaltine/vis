import blessed 
terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position 
import os

os.system('clear') 

#global variables
current_button_index = 1 

def menu_bg(filename:str): 
    draw(filename, Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')

def menu_title(filename:str): 
    left_pos = "calc(50% - 70)"
    top_pos = 4 
    draw(filename, Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def start_text(filename:str): 
    left_pos = "calc(50% + 99)"
    bottom_pos = 9
    draw(filename, Position.Relative(left=left_pos, bottom=bottom_pos), (None, None), 'crop')

def main_logo_bg(filename:str): 
    draw(filename, pos=Position.Relative(left="calc(30% - 1ch)", bottom="calc(50% - 10ch)"))

def viscord_logo_bg(filename:str): 
    draw(filename, pos=Position.Relative(left="calc(30% - 15ch)", bottom="calc(50% - 10ch)"))

def apps_text(filename:str): 
    left_pos = "calc(50% + 95)"
    top_pos = 3
    draw(filename, Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')

def draw_apps(num_button_index): 
        viscord_logo_bg('assets/viscord_logo_copy.png')
   

def create_menu(): 
          
          menu_bg('assets/menu_bg.png')
          menu_title('assets/main_menu_title_2_better.png')
          start_text('assets/start.png')
          main_logo_bg('assets/updated_logo_2.png')

          with terminal.hidden_cursor():

            while True:
                with terminal.cbreak():
                    val = terminal.inkey(timeout=1)
                    if val == 'q':
                        os.system('clear')
                        break 
                    else:
                        update_cursor_movement(val) 

def update_cursor_movement(val): 
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
                current_button_index=1
        
        if changed: 
             draw_apps(current_button_index)


        if val.name == 'KEY_ENTER': 
            menu_bg('assets/menu_bg.png')
            apps_text('assets/app.png')
            draw_apps(0)
            
        if val.name == 'KEY_ESCAPE':
            menu_bg('assets/menu_bg.png')
            menu_title('assets/main_menu_title_2_better.png')
            start_text('assets/start.png')
            main_logo_bg('assets/updated_logo_2.png')

#function call 
create_menu()