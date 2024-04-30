import blessed 
import signal 
Menuterm = blessed.Terminal()

def draw_rect(width, height):
    for y in range(height):
        for x in range(width):
            if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                print(Menuterm.on_blue2(Menuterm.blue2(' ')), end='')
            else:
                print(Menuterm.on_blue2(' '), end='')

def menu_title(title:str): 
    print(Menuterm.move_yx(1,54) + Menuterm.yellow_on_blue2(Menuterm.underline(Menuterm.bold(title)))) 
    print(Menuterm.move_yx(Menuterm.height, Menuterm.width))


draw_rect(Menuterm.width, Menuterm.height)
menu_title("VEOMETRY DASH")