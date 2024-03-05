import blessed
import os
import curses
from time import sleep
from utils import fcode
term = blessed.Terminal()

BLOCK_ELEMENT = "█"

BG_COLOR = "#0091ff"
GROUND_COLOR = "#0d7bf1"
BLOCK_COLOR_1 = "#222"
BLOCK_COLOR_2 = "#333"
SPIKE_COLOR_1 = "#444"
SPIKE_COLOR_2 = "#555"


objects = {
    "spike": [
        f"{fcode(background=BG_COLOR)} {fcode(foreground='000')}/\\{fcode(background=BG_COLOR)} ",
        f"{fcode(foreground='000')}/__\\"
    ],
    "block": [
        f"{fcode(background=BLOCK_COLOR_1)}    ",
        f"{fcode(background=BLOCK_COLOR_2)}    "
    ]
}

def draw_obj(y, x, obj_name):
    """
    Draws a temporary spike texture at the specified row, column.
    """

    # if near edge, dont render
    # TODO - we can add partial rendering later
    if x < 0 or y < 0 or x > term.width or y > term.height:
        return

    obj_texture = objects[obj_name]

    for i in range(len(obj_texture)):

        # a clever way to not have to rerender the entire bg every time.
        # drawing another bg-colored char makes it "cover up" the old characters
        refresh_optimization = f"{fcode(background=BG_COLOR)} "

        print(term.move_yx(y + i, x) + obj_texture[i] + refresh_optimization)


class Rect:
    """
    Draws a rectangle on the screen at the specified position.
    """
    def __init__(self, left, top, right, bottom, bg_color=None):
        """
        future - `bg_color` can be an rgb tuple or any 3/6-digit hex code (# optional)
        """
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.fcode = fcode(background=bg_color)

        self.wcopy = 0
        self.hcopy = 0

    def render(self, width, height):

        self.wcopy = width
        self.hcopy = height

        width_px = (self.right - self.left) * width // 100

        with term.hidden_cursor():
            for y in range(min(height, 1+(height * (self.bottom - self.top) // 100))):
                print(term.move(height * self.top // 100 + y, width * self.left // 100) + f"{self.fcode} "*width_px)
            
            
    def print_at(self, y, x, text):
        print(term.move_yx(self.top * self.hcopy // 100 + 1 + y, (self.left * self.wcopy // 100) + 1 + x) + text)

main = [
    Rect(0, 0, 100, 100, BG_COLOR), # bg
    Rect(0, 70, 100, 100 , GROUND_COLOR), # ground
]

w = term.width 
h = term.height

[item.render(w,h) for item in main]

with term.hidden_cursor():
    for i in range(100):
        w = term.width 
        h = term.height

        # os.system("cls")
        # print(term.clear + term.home)
        term.clear()

        # [item.render(w,h) for item in main]
        
        draw_obj(17, 16-i, "block")
        draw_obj(17, 20-i, "spike")
        draw_obj(17, 24-i, "spike")
        draw_obj(17, 28-i, "spike")
        draw_obj(17, 32-i, "block")
        draw_obj(15, 32-i, "block")

        draw_obj(15, 120-i, "block")
        draw_obj(13, 124-i, "block")
        draw_obj(15, 128-i, "block")
        draw_obj(15, 132-i, "spike")
        
        sleep(1/30)