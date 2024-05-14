from blessed import Terminal
import os
from draw_utils import fcode
from typing import Literal

terminal = Terminal()

def draw_square(width: int, height: int, x: int, y: int, color: str | tuple) -> None:
    """
    Draws a rectangle on the screen (an isoceles triangle pointing upwards or sideways)
    
    Pass in `color` as a hex code, a tuple of rgb values, or a predefined color name (see `fcode` method)
    """
    
    for i in range(y, y+height):
        print(terminal.move_yx(i, x) + fcode(color)+"█"*width + terminal.normal, end="")

def draw_spike(height, x: int, y: int, color: str, orientation: Literal["right", "left", "up"] = "up") -> None:
    """
    Draws a spike on the screen (an isoceles triangle pointing upwards or sideways)
    
    Pass in `color` as a hex code, a tuple of rgb values, or a predefined color name (see `fcode` method)
    """
    
    assert orientation in ['right', 'left', 'up'], "[draw_spike]: Invalid orientation. Must be 'right', 'left', or 'up'"
    
    if orientation == 'right':

        # If orient_right is True, the "height" will be considered the max base length, so we will draw a spike sideways

        for i in range(1, height+1):
            dots=fcode(color)
            for k in range(int(height*0.4)):
                
                for j in range(i):
                    dots+="█"
            print(terminal.move_yx(y+i-1, x) + dots+terminal.normal, end="")
        
        for i in range(height-1, 0, -1):
            dots=f"{fcode(color)}"
            for k in range(int(height*0.4)):
                for j in range(i):
                    dots+="█"
            print(terminal.move_yx(y+height+(height-i-1), x) + dots+terminal.normal, end="")

    elif orientation == 'left':

        # If orient_left is True, the "height" will be considered the max base length, so we will draw a spike sideways

        for i in range(1, height+1):
            line=f"{terminal.on_black}"
            for k in range(int(height*0.4)):
                
                for j in range(height-i):
                    line+=" "
                for j in range(i):
                    line+=f"{fcode(color)}█"
            print(terminal.move_yx(y+i-1, x) + line+terminal.normal, end="")
        
        for i in range(height-1, 0, -1):
            line=f"{terminal.on_black}"
            for k in range(int(height*0.4)):
                for j in range(height-i):
                    line+=" "
                
                for j in range(i):
                    line+=f"{fcode(color)}█"
            print(terminal.move_yx(y+height+(height-i-1), x) + line+terminal.normal, end="")
    
    else:
        # Generating an ascii pyramid line by line
        for i in range(y, y+height):
            spaces=""
            for j in range(height-(i-y)):
                spaces+=f"{terminal.on_black} "
            dots=""
            for j in range(2*(i-y)+1):
                dots+="█"
            line=f"{fcode(color)}"+spaces+ dots + spaces + terminal.normal

            print(terminal.move_yx(i, x) + line, end="")
    
# Writes text on the screen, assuming the background color is blue
def draw_text(text:str, x:int, y:int, bold=False, underline=False, text_highlight_color='black'):
    line=terminal.move_xy(x, y)
    if bold:
        line+=terminal.bold
    if underline:
        line+=terminal.underline
    
    on_color=getattr(terminal, 'on_'+text_highlight_color)
    line+=on_color(text)       
    print(line)

def draw_orb(width:int, height:int, x:int, y:int, type:str) -> None:
    """
    Draws an orb on the screen - either:
    blue (string "turquoise" since the blue color is being used for something else), purple, or yellow
    """
    alt_color='dark_'+type
    draw_square(width, height, x, y, 'white')
    draw_square(int(width/2), int(height/2), x+int(width/4)+1, y, type)
    draw_square(int(width/2), int(height/2), x+int(width/4)+1, y+int(height/2), alt_color)

# Main function to generate the bottom menu
def draw_bottom_menu():
    
   # This clears the screen

    os.system('cls')

    # Setting bg color to blue

    draw_square(terminal.width, terminal.height, 0, 0, 'blue')

    # Drawing the main blue rectangle on the screen

    draw_square(terminal.width, int(terminal.height*0.41)+1, 0, int(terminal.height*0.6), 'black')

    while True:

        # Writing the "Bindings" text onto the screen

        title_text='LEVEL EDITOR BINDINGS'
        draw_text(title_text, int((terminal.width-len(title_text))/2)-1,int(terminal.height*0.63), True)

        # Writing WASD bindings to the screen

        wasd_text='Move Screen:'
        draw_text(wasd_text, int(terminal.width*0.02), int(terminal.height*0.68))

        w_text='   Up: [W]'
        draw_text(w_text, int(terminal.width*0.02), int(terminal.height*0.7))

        a_text='   Left: [A]'
        draw_text(a_text, int(terminal.width*0.02), int(terminal.height*0.72))

        s_text='   Down: [S]'
        draw_text(s_text, int(terminal.width*0.02), int(terminal.height*0.75))

        d_text='   Right: [D]'
        draw_text(d_text, int(terminal.width*0.02), int(terminal.height*0.77))

        # Writing arrow key bindings to the screen

        wasd_text='Move Selected Object:'
        draw_text(wasd_text, int(terminal.width*0.02), int(terminal.height*0.81))

        up_text='   Up: [↑]'
        draw_text(up_text, int(terminal.width*0.02), int(terminal.height*0.83))

        left_text='   Left: [←]'
        draw_text(left_text, int(terminal.width*0.02), int(terminal.height*0.85))

        down_text='   Down: [↓]'
        draw_text(down_text, int(terminal.width*0.02), int(terminal.height*0.89))

        right_text='   Right: [→]'
        draw_text(right_text, int(terminal.width*0.02), int(terminal.height*0.9))

        # Drawing the block onto the screen

        draw_square(int(terminal.width*0.08), int(terminal.height*0.14), int(terminal.width*0.25), int(terminal.height*0.68), 'red')

        # Writing the "Toggle Block" text onto the screen

        block_text='Toggle Block: [B]'
        draw_text(block_text, int(terminal.width*0.245), int(terminal.height*0.83))

        # Drawing a spike onto the screen

        draw_spike(int(terminal.height*0.14), int(terminal.width*0.39), int(terminal.height*0.68), 'green')

        # Writing the "Toggle Spike" text onto the screen

        spike_text='Toggle Spike: [S]'
        draw_text(spike_text, int(terminal.width*0.385), int(terminal.height*0.83))

        # Drawing a blue orb onto the screen

        draw_orb(int(terminal.width*0.07), int(terminal.height*0.14), int(terminal.width*0.54), int(terminal.height*0.68), 'turquoise')

        # Writing the "Toggle Blue Orb" text onto the screen

        blue_orb_text='Toggle Blue Orb: [O]'
        draw_text(blue_orb_text, int(terminal.width*0.52), int(terminal.height*0.83))

        # Drawing a purple orb onto the screen

        draw_orb(int(terminal.width*0.07), int(terminal.height*0.14), int(terminal.width*0.69), int(terminal.height*0.68), 'purple')

        # Writing the "Toggle Purple Orb" text onto the screen

        purple_orb_text='Toggle Purple Orb: [P]'
        draw_text(purple_orb_text, int(terminal.width*0.665), int(terminal.height*0.83))

        # Drawing a yellow orb onto the screen

        draw_orb(int(terminal.width*0.07), int(terminal.height*0.14), int(terminal.width*0.845)+1, int(terminal.height*0.68), 'yellow')

        # Writing the "Toggle Yellow Orb" text onto the screen

        purple_orb_text='Toggle Yellow Orb: [Y]'
        draw_text(purple_orb_text, int(terminal.width*0.825), int(terminal.height*0.83))

        # Writing other bindings below the shapes

        save_text='Save Level: [X]'
        draw_text(save_text, int(terminal.width*0.245), int(terminal.height*0.9))

        load_text='Load Level: [L]'
        draw_text(load_text, int(terminal.width*0.39), int(terminal.height*0.9))

        undo_text='Undo: [Z]'
        draw_text(undo_text, int(terminal.width*0.55), int(terminal.height*0.9))

        clear_text='Clear All: [C]'
        draw_text(clear_text, int(terminal.width*0.685), int(terminal.height*0.9))

        test_text='Test Level: [T]'
        draw_text(test_text, int(terminal.width*0.84), int(terminal.height*0.9))

        toggle_placement_text='Object Placement/Pickup: [Enter]'
        draw_text(toggle_placement_text, int(terminal.width*0.265), int(terminal.height*0.96))

        delete_text='Delete Selected Object: [Backspace]'
        draw_text(delete_text, int(terminal.width*0.63), int(terminal.height*0.96))
        