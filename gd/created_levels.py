import random

import blessed
from bottom_menu import *
import os
import logging

terminal = blessed.Terminal()

os.system('cls')

colors=[('blue', 'gray'), ('red', 'gray')]


level_file_names=[]
def update_list_of_level_files(file_type='.level'):
    
    global level_file_names

    for root, dirs, files in os.walk('levels'):
       
        for file in files:
            
            if file.endswith(file_type):
                # print whole path of files
                filename=os.path.join(root, file)
                #logging.error('name   ' + filename)
                filename=filename[filename.index('\\')+1:]
                level_file_names.append(filename)
                

    if len(level_file_names)==0:
        level_file_names.append('You have not created any levels')
  

def draw_created_level(level_name:str, width:int, height:int, x:int, y:int, color1:str, color2:str):

    draw_rect(color1, Position.Relative(left=x, top=y), width, height)
    draw_rect(color2, Position.Relative(left=int(x+(x*0.2)), top=int(y+(y*0.1))), int(width*0.95), int(height*0.9))
    draw_text(level_name, int(x+(width-len(level_name))*0.5), int(y+(height*0.2)), True, False, 'white', color2)
    #draw_text(level_description, int(x+(width-len(level_description))*0.5), int(y+(height*0.5)), False, False, 'white', color2)


def draw_created_levels():

    text=''
    level_path=level_file_names[0]

    if level_path=='You have not created any levels':
        text=level_path
    else:
        color=random.choice(colors)
        level_name=level_path[level_path.index('\\')+1:level_path.index('.level')]
        level_name=level_name[0].upper()+level_name[1:]
        draw_created_level(level_name, int(GD.term.width*0.8), int(GD.term.height*0.6), int(GD.term.width*0.1), int(GD.term.height*0.3), color[0], color[1])

def reset_level(width=int(GD.term.width*0.8), height=int(GD.term.height*0.6), x=int(GD.term.width*0.1), y=int(GD.term.height*0.3)):
    draw_rect('black', Position.Relative(left=x, top=y), width, height)


def init_created_levels_page(terminal):
    update_list_of_level_files('.level')
    # draw fullscreen bg
    draw_rect("#000000", Position.Relative(0, 0, 0, 0))

    level_path=level_file_names[0]
    color=colors[0]
    if level_path=='You have not created any levels':
        draw_text(level_path, int(terminal.width*0.4), int(terminal.height*0.5))
    else:
        selector_text='Select a level by navigating with the arrow keys. Hit p to play a level and e to edit.'
        draw_text(selector_text, int(terminal.width*0.23), int(terminal.height*0.2))
        draw_spike(int(terminal.width*0.025), int(terminal.width*0.95), int(terminal.height*0.5), 'white', 'right')
        draw_spike(int(terminal.width*0.025), int(terminal.width*0.03), int(terminal.height*0.5), 'white', 'left')
        level_name=level_path[0:level_path.index('.')]
        level_name=level_path[0].upper()+level_name[1:]
        draw_created_level(level_name, int(terminal.width*0.8), int(terminal.height*0.6), 
                   int(terminal.width*0.1), int(terminal.height*0.3), color[0], color[1])