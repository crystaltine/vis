import blessed 
from PIL import Image
Menuterm = blessed.Terminal()

colors={
    'blue':Menuterm.blue,
    'red':Menuterm.red,
    'green':Menuterm.green4,
    'purple':Menuterm.magenta2,
    'pink':Menuterm.pink,
    'yellow':Menuterm.gold,
    'white':Menuterm.ghostwhite,
    'turquoise':Menuterm.turquoise1,
    'dark_yellow':Menuterm.gold3,
    'dark_turquoise':Menuterm.turquoise4,
    'dark_purple':Menuterm.darkmagenta,
    'black':Menuterm.black
}

def draw_rect(width:int, height:int):
    """
    using the desginated width and height passed in as a parameter, 
    a filled, blue rectangle will be drawn in the terminal 
    """
    for y in range(height):
        for x in range(width):
            if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                print(Menuterm.on_blue2(Menuterm.blue2(' ')), end='')
            else:
                print(Menuterm.on_blue2(' '), end='')

def print_text(title:str, x:int, y:int): 
    """
    Allows user to create a title for their blue filled in rectangle 
    """
    print(Menuterm.move_yx(y,x) + Menuterm.yellow_on_blue2(Menuterm.underline(Menuterm.bold(title)))) 
    print(Menuterm.move_yx(Menuterm.height, Menuterm.width))

def draw_square(width:int, height:int, x: int, y: int, color:str) -> None:

    for i in range(y, y+height):
        print(Menuterm.move_yx(i, x) + colors[color]+"█"*width + Menuterm.normal, end="")

def draw_spike_with_rotation(height: int, x: int, y: int, color: str, rotation: str = 'clockwise'):
    # Generating an ascii pyramid line by line

    if rotation == 'clockwise':
        range_start = y
        range_end = y + height
        range_step = 1
    elif rotation == 'counterclockwise':
        range_start = y + height - 1
        range_end = y - 1
        range_step = -1

    for i in range(range_start, range_end, range_step):
        spaces = ""
        for j in range(abs(y - i)):
            spaces+=f"{Menuterm.on_green4}"
        dots = ""
        for j in range(2 * (abs(y - i)) + 1):
            dots += "█"
        line = f"{colors[color]}" + spaces + dots + spaces + Menuterm.normal

        print(Menuterm.move_yx(i, x) + line, end="")

#creates the veometry dash menu# 
draw_rect(Menuterm.width, Menuterm.height)
#draws the first square + the character icon 
draw_square(30,15,5,20,'green')
draw_square(16,8,12,24, 'black')
draw_square(4,2,15,25,'green')
draw_square(4,2,21,25,'green')
draw_square(10,2,15,29,'green')
#draws the second square 
draw_square(40,20,41,17,'green')
draw_spike_with_rotation(15, 49, 20, 'black', 'clockwise')
#draws the third square 
draw_square(30,15,87,20,'green')
#puts the title on the menu screen 
print_text("VEOMETRY DASH", 54,1)


