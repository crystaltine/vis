from bottom_menu import *

os.system('cls')

levels=[{'level_name':'TEST LEVEL 1',
         'level_description':'This is a random test level for demo purposes',
         'color1':'blue',
         'color2':'gray',
         'path': 'test.level'}, 
        
        {'level_name':'TEST LEVEL 2',
         'level_description':'This is a random test level for demo purposes version 2',
         'color1':'red',
         'color2':'gray',
         'path':'test2.level'}
    ]
    
def draw_level(level_name:str, level_description:str, width:int, height:int, x:int, y:int, color1:str, color2:str):

    draw_rect(color1, Position.Relative(left=x, top=y), width, height)
    draw_rect(color2, Position.Relative(left=int(x+(x*0.2)), top=int(y+(y*0.1))), int(width*0.95), int(height*0.9))
    draw_text(level_name, int(x+(width-len(level_name))*0.5), int(y+(height*0.2)), True, False, 'white', color2)
    draw_text(level_description, int(x+(width-len(level_description))*0.5), int(y+(height*0.5)), False, False, 'white', color2)


def draw_level_selector():

    test_level_description='This is a random test level for demo purposes'
    draw_level('TEST LEVEL 1', test_level_description, int(GD.term.width*0.8), int(GD.term.height*0.6), int(GD.term.width*0.1), int(GD.term.height*0.3), 'blue', 'gray')
    while True:
        draw_text('', 0, 0)

def reset_level(width=int(GD.term.width*0.8), height=int(GD.term.height*0.6), x=int(GD.term.width*0.1), y=int(GD.term.height*0.3)):
    draw_rect('black', Position.Relative(left=x, top=y), width, height)


def init_level_select_page(terminal):
    # draw fullscreen bg
    draw_rect("#000000", Position.Relative(0, 0, 0, 0))

    selector_text='Select a level by navigating with the arrow keys and hitting enter once you have chosen a level'
    draw_text(selector_text, int(terminal.width*0.23), int(terminal.height*0.2))

    # Drawing the two arrows on each side of the level

    draw_spike(int(terminal.width*0.025), int(terminal.width*0.95), int(terminal.height*0.5), 'white', 'right')
    draw_spike(int(terminal.width*0.025), int(terminal.width*0.03), int(terminal.height*0.5), 'white', 'left')

    level_info=levels[0]
    draw_level(level_info['level_name'], level_info['level_description'], int(terminal.width*0.8), int(terminal.height*0.6), 
                   int(terminal.width*0.1), int(terminal.height*0.3), level_info['color1'], level_info['color2'])
    
#draw_level_selector()
