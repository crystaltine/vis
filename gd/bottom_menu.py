from GD import GD
import os
from draw_utils import fcode, print2, draw_rect, Position
from typing import Literal

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
            print2(GD.term.move_yx(y+i-1, x) + dots+GD.term.normal)
        
        for i in range(height-1, 0, -1):
            dots=f"{fcode(color)}"
            for k in range(int(height*0.4)):
                for j in range(i):
                    dots+="█"
            print2(GD.term.move_yx(y+height+(height-i-1), x) + dots+GD.term.normal)

    elif orientation == 'left':

        # If orient_left is True, the "height" will be considered the max base length, so we will draw a spike sideways

        for i in range(1, height+1):
            line=f"{GD.term.on_black}"
            for k in range(int(height*0.4)):
                
                for j in range(height-i):
                    line+=" "
                for j in range(i):
                    line+=f"{fcode(color)}█"
            print2(GD.term.move_yx(y+i-1, x) + line+GD.term.normal)
        
        for i in range(height-1, 0, -1):
            line=f"{GD.term.on_black}"
            for k in range(int(height*0.4)):
                for j in range(height-i):
                    line+=" "
                
                for j in range(i):
                    line+=f"{fcode(color)}█"
            print2(GD.term.move_yx(y+height+(height-i-1), x) + line+GD.term.normal)
    
    else:
        # Generating an ascii pyramid line by line
        for i in range(y, y+height):
            spaces=""
            for j in range(height-(i-y)):
                spaces+=f"{GD.term.on_black} "
            dots=""
            for j in range(2*(i-y)+1):
                dots+="█"
            line=f"{fcode(color)}"+spaces+ dots + spaces + GD.term.normal

            print2(GD.term.move_yx(i, x) + line)
    
# Writes text on the screen, assuming the background color is blue
def draw_text(text:str, x:int, y:int, bold=False, underline=False, color: str | tuple = "#ffffff", bg_color: str | tuple = None):
    line=GD.term.move_xy(x, y)
    if bold:
        line+=GD.term.bold
    if underline:
        line+=GD.term.underline
    
    line += fcode(color, bg_color) + text + GD.term.normal
    print2(line)

ORB_COLORS = {
    'turquoise': ['#00ffff', '#00cccc'],
    'purple': ['#ee00ff', '#bb00cc'],
    'yellow': ['#ffee00', '#ccbb00'],
}
def draw_orb(width:int, height:int, x:int, y:int, type:str) -> None:
    """
    Draws an orb on the screen - either:
    blue (string "turquoise" since the blue color is being used for something else), purple, or yellow
    """
    draw_rect('white', Position.Relative(left=x,top=y), width, height)
    draw_rect(ORB_COLORS[type][0], Position.Relative(left=x+int(width/4)+1, top=y),int(width/2), int(height/2))
    draw_rect(ORB_COLORS[type][1], Position.Relative(left=x+int(width/4)+1, top=y+int(height/2)), int(width/2), int(height/2))

# Main function to generate the bottom menu
def draw_bottom_menu():
    
   # This clears the screen

    os.system('clear')

    # Setting bg color to blue
    draw_rect('blue', Position.Relative(0,0,0,0))

    # Drawing the main blue rectangle on the screen
    draw_rect('black', Position.Relative(left=0, top=int(GD.term.height*0.6)), GD.term.width, int(GD.term.height*0.41)+1)

    while True:

        # Writing the "Bindings" text onto the screen

        title_text='LEVEL EDITOR BINDINGS'
        draw_text(title_text, int((GD.term.width-len(title_text))/2)-1,int(GD.term.height*0.63), True)

        # Writing WASD bindings to the screen

        wasd_text='Move Screen:'
        draw_text(wasd_text, int(GD.term.width*0.02), int(GD.term.height*0.68))

        w_text='   Up: [W]'
        draw_text(w_text, int(GD.term.width*0.02), int(GD.term.height*0.7))

        a_text='   Left: [A]'
        draw_text(a_text, int(GD.term.width*0.02), int(GD.term.height*0.72))

        s_text='   Down: [S]'
        draw_text(s_text, int(GD.term.width*0.02), int(GD.term.height*0.75))

        d_text='   Right: [D]'
        draw_text(d_text, int(GD.term.width*0.02), int(GD.term.height*0.77))

        # Writing arrow key bindings to the screen

        wasd_text='Move Selected Object:'
        draw_text(wasd_text, int(GD.term.width*0.02), int(GD.term.height*0.81))

        up_text='   Up: [↑]'
        draw_text(up_text, int(GD.term.width*0.02), int(GD.term.height*0.83))

        left_text='   Left: [←]'
        draw_text(left_text, int(GD.term.width*0.02), int(GD.term.height*0.85))

        down_text='   Down: [↓]'
        draw_text(down_text, int(GD.term.width*0.02), int(GD.term.height*0.89))

        right_text='   Right: [→]'
        draw_text(right_text, int(GD.term.width*0.02), int(GD.term.height*0.9))

        # Drawing the block onto the screen

        draw_rect('red', Position.Relative(left=int(GD.term.width*0.25), top=int(GD.term.height*0.68)), int(GD.term.width*0.08), int(GD.term.height*0.14))

        # Writing the "Toggle Block" text onto the screen

        block_text='Toggle Block: [B]'
        draw_text(block_text, int(GD.term.width*0.245), int(GD.term.height*0.83))

        # Drawing a spike onto the screen

        draw_spike(int(GD.term.height*0.14), int(GD.term.width*0.39), int(GD.term.height*0.68), 'green')

        # Writing the "Toggle Spike" text onto the screen

        spike_text='Toggle Spike: [S]'
        draw_text(spike_text, int(GD.term.width*0.385), int(GD.term.height*0.83))

        # Drawing a blue orb onto the screen

        draw_orb(int(GD.term.width*0.07), int(GD.term.height*0.14), int(GD.term.width*0.54), int(GD.term.height*0.68), 'turquoise')

        # Writing the "Toggle Blue Orb" text onto the screen

        blue_orb_text='Toggle Blue Orb: [O]'
        draw_text(blue_orb_text, int(GD.term.width*0.52), int(GD.term.height*0.83))

        # Drawing a purple orb onto the screen

        draw_orb(int(GD.term.width*0.07), int(GD.term.height*0.14), int(GD.term.width*0.69), int(GD.term.height*0.68), 'purple')

        # Writing the "Toggle Purple Orb" text onto the screen

        purple_orb_text='Toggle Purple Orb: [P]'
        draw_text(purple_orb_text, int(GD.term.width*0.665), int(GD.term.height*0.83))

        # Drawing a yellow orb onto the screen

        draw_orb(int(GD.term.width*0.07), int(GD.term.height*0.14), int(GD.term.width*0.845)+1, int(GD.term.height*0.68), 'yellow')

        # Writing the "Toggle Yellow Orb" text onto the screen

        purple_orb_text='Toggle Yellow Orb: [Y]'
        draw_text(purple_orb_text, int(GD.term.width*0.825), int(GD.term.height*0.83))

        # Writing other bindings below the shapes

        save_text='Save Level: [X]'
        draw_text(save_text, int(GD.term.width*0.245), int(GD.term.height*0.9))

        load_text='Load Level: [L]'
        draw_text(load_text, int(GD.term.width*0.39), int(GD.term.height*0.9))

        undo_text='Undo: [Z]'
        draw_text(undo_text, int(GD.term.width*0.55), int(GD.term.height*0.9))

        clear_text='Clear All: [C]'
        draw_text(clear_text, int(GD.term.width*0.685), int(GD.term.height*0.9))

        test_text='Test Level: [T]'
        draw_text(test_text, int(GD.term.width*0.84), int(GD.term.height*0.9))

        toggle_placement_text='Object Placement/Pickup: [Enter]'
        draw_text(toggle_placement_text, int(GD.term.width*0.265), int(GD.term.height*0.96))

        delete_text='Delete Selected Object: [Backspace]'
        draw_text(delete_text, int(GD.term.width*0.63), int(GD.term.height*0.96))
        