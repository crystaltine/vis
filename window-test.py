import blessed
import os
term = blessed.Terminal()
print(term.clear)

from math import floor, ceil

global corners
corners = {}

class Box:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.children = []
        self.title = "Window Title"

        self.gl = 0
        self.gt = 0

        self.wcopy = 0
        self.hcopy = 0

    def render(self, gl, gt, width, height):
        global corners

        self.gl = gl
        self.gt = gt

        self.wcopy = width
        self.hcopy = height

        with term.hidden_cursor():
            print(term.move(gt + height * self.top // 100, gl + width * self.left // 100) + "─" * (width * (self.right - self.left) // 100))
            for y in range(1+(height * (self.bottom - self.top) // 100)):
                print(term.move(gt + (height * self.top // 100) + y, gl + width * self.left // 100) + "│")
                print(term.move(gt + (height * self.top // 100) + y, gl + width * self.right // 100) + "│")
            print(term.move(gt + (height * self.bottom // 100), gl + width * self.left // 100) + "─" * (width * (self.right - self.left) // 100))
            
            
            
            if (gt + height * self.top // 100, gl + width * self.left // 100) not in corners:
                corners[(gt + height * self.top // 100, gl + width * self.left // 100)] = set()
            corners[(gt + height * self.top // 100, gl + width * self.left // 100)] |= {"r", "d"}

            if (gt + height * self.top // 100, gl + width * self.right // 100) not in corners:
                corners[(gt + height * self.top // 100, gl + width * self.right // 100)] = set()
            corners[(gt + height * self.top // 100, gl + width * self.right // 100)] |= {"l", "d"}

            if (gt + (height * self.bottom // 100), gl + width * self.left // 100) not in corners:
                corners[(gt + (height * self.bottom // 100), gl + width * self.left // 100)] = set()
            corners[(gt + (height * self.bottom // 100), gl + width * self.left // 100)] |= {"r", "u"}

            if (gt + (height * self.bottom // 100), gl + width * self.right // 100) not in corners:
                corners[(gt + (height * self.bottom // 100), gl + width * self.right // 100)] = set()
            corners[(gt + (height * self.bottom // 100), gl + width * self.right // 100)] |= {"l", "u"}

        for child in self.children:
            child.render(
                gl + (self.left * width // 100),
                gt + (self.top * height // 100), 
                (width * (self.right - self.left) // 100), (height * (self.bottom - self.top) // 100))

        #print(term.move(gt + (self.top * height // 100) + 1, gl + (self.left * width // 100) + int(width // 2) - len(self.title) // 2) + self.title)
        #print(term.move_yx(gt + (self.top * height // 100) + 1, gl + (self.left * width // 100) + 1) + "Hiiiiii >_< :3")
        if (width * (self.right - self.left) // 100) > len(self.title):
            print(term.move_yx(self.gt + (self.top * self.hcopy // 100) + 1, self.gl + (self.left * self.wcopy // 100) + 1 + (width * (self.right - self.left) // 100) // 2 - len(self.title) // 2) + term.black_on_white + self.title + term.normal)

    def print_at(self, y, x, text):
        print(term.move_yx(self.gt + (self.top * self.hcopy // 100) + 1 + y, self.gl + (self.left * self.wcopy // 100) + 1 + x) + text)


main = [
    Box(0, 20, 10, 90),
    Box(20, 100, 10, 70),
    Box(20, 100, 70, 90)
]


for item in main:
    item.render(0, 0, term.width, term.height)

main[1].print_at(5, 5, "hello world")

#b.print_at(0, 5, "Hiiiiii >_< :3")

lx = term.width
ly = term.height

for item in corners:
    s = corners[item]
    char = ""
    if s == {"r", "u"}:
        char = "└"
    if s == {"l", "u"}:
        char = "┘"
    if s == {"l", "d"}:
        char = "┐"
    if s == {"r", "d"}:
        char = "┌"
    if s == {"l", "u", "r"}:
        char = "┴"
    if s == {"l", "d", "r"}:
        char = "┬"
    if s == {"l", "u", "d"}:
        char = "┤"
    if s == {"r", "u", "d"}:
        char = "├"
    if s == {"l", "u", "r", "d"}:
        char = "┼"
    print(term.move_yx(item[0], item[1]) + char)
    #print(item)
    

while True:
    w = term.width 
    h = term.height
    if lx != w or ly != h:
        os.system("cls")
        print(term.home + term.clear)
        corners = {}
        for item in main:
            item.render(0, 0, w, h)

        for item in corners:
            s = corners[item]
            char = ""
            if s == {"r", "u"}:
                char = "└"
            if s == {"l", "u"}:
                char = "┘"
            if s == {"l", "d"}:
                char = "┐"
            if s == {"r", "d"}:
                char = "┌"
            if s == {"l", "u", "r"}:
                char = "┴"
            if s == {"l", "d", "r"}:
                char = "┬"
            if s == {"l", "u", "d"}:
                char = "┤"
            if s == {"r", "u", "d"}:
                char = "├"
            if s == {"l", "u", "r", "d"}:
                char = "┼"
            print(term.move(*item) + char)

        lx = w
        ly = h