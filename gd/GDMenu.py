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
    'black':Menuterm.black, 
    'sienna4':Menuterm.sienna4,
    'gray' :Menuterm.gray52
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

def draw_spike(height, x:int, y:int, color:str='white'):

    # Generating an ascii pyramid line by line

    for i in range(y, y+height):
        spaces=""
        for j in range(height-(i-y)):
            spaces+=f"{Menuterm.on_green4} "
        dots=""
        for j in range(2*(i-y)+1):
            dots+="█"
        line=f"{colors[color]}"+spaces+ dots + spaces +  Menuterm.normal

        print(Menuterm.move_yx(i, x) + line, end="")

#creates the veometry dash menu# 
draw_rect(Menuterm.width, Menuterm.height)
#draws the first square + the character icon 
draw_square(30,15,5,20,'green')
draw_square(16,8,12,24, 'yellow')
draw_square(4,2,15,25,'black')
draw_square(4,2,21,25,'black')
draw_square(10,2,15,29,'black')
#draws the second square 
draw_square(40,20,41,17,'green')
draw_spike(15, 45, 20, 'white')
#draws the third square 
draw_square(30,15,87,20,'green')
draw_square(5,10,99,24, 'sienna4')
draw_square(15,3,94,22, 'gray')
#puts the title on the menu screen 
print_text("VEOMETRY DASH", 54,1)


