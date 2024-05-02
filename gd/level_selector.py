import blessed
from bottom_menu import *

terminal = Terminal()
os.system('cls')

levels=[{'level_name':'TEST LEVEL 1',
         'level_description':'This is a random test level for demo purposes',
         'color1':'blue',
         'color2':'grey49',
         'file': 'run_gd.py'}, 
        
        {'level_name':'TEST LEVEL 2',
         'level_description':'This is a random test level for demo purposes version 2',
         'color1':'red',
         'color2':'grey49',
         'file':''}
    ]
    



def draw_level(level_name:str, level_description:str, width:int, height:int, x:int, y:int, color1:str, color2:str):

    draw_square(width, height, x, y, color1)
    draw_square(int(width*0.95), int(height*0.9), int(x+(x*0.2)), int(y+(y*0.1)), color2)
    draw_text(level_name, int(x+(width-len(level_name))*0.5), int(y+(height*0.2)), True, False, color2)
    draw_text(level_description, int(x+(width-len(level_description))*0.5), int(y+(height*0.5)), False, False, color2)


def draw_level_selector():

    with terminal.hidden_cursor():
        test_level_description='This is a random test level for demo purposes'
        draw_level('TEST LEVEL 1', test_level_description, int(terminal.width*0.8), int(terminal.height*0.6), int(terminal.width*0.1), int(terminal.height*0.3), 'blue', 'grey49')
        while True:
           draw_text('', 0, 0)

def reset_level(width=int(terminal.width*0.8), height=int(terminal.height*0.6), x=int(terminal.width*0.1), y=int(terminal.height*0.3)):

    draw_square(width, height, x, y, 'black')


#draw_level_selector()
