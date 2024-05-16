import blessed 
terminal = blessed.Terminal()
from img2term.main import draw 
from draw_utils import Position
import os

os.system('clear')

class level_editor_menu: 
    def draw_menu_background(): 
        draw('assets/menu_bg_1.png', Position.Relative(top=0, left=0), (terminal.width, terminal.height*2), 'scale')
    def draw_play_button(): 
            draw(f"assets/main_menu/start_button.png", pos=Position.Relative(left="calc(50% - 18ch)", bottom="calc(50% - 10ch)"))
    def draw_menu_title(): 
        left_pos = "calc(50% - 70)"
        top_pos = 4 # arbitrary value
        draw('assets/menu_title_1_editable.png', Position.Relative(left=left_pos, top=top_pos), (None, None), 'crop')





#function calls 
    draw_menu_background()
    draw_menu_title() 

    draw_play_button() 
    

    


