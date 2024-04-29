import blessed 

Menuterm = blessed.Terminal()

def draw_rect(width, height):
    for y in range(height):
        for x in range(width):
            if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                print(Menuterm.on_blue2(Menuterm.blue2(' ')), end='')
            else:
                print(Menuterm.on_blue2(' '), end='')
        print()
    
draw_rect(Menuterm.width, Menuterm.height)


