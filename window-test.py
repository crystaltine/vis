import blessed
term = blessed.Terminal()
print(term.clear)

from math import floor, ceil

class Box:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.children = []

    def render(self, gl, gt, width, height):

        with term.hidden_cursor():
            print(term.move(gt + height * self.top // 100, gl + width * self.left // 100) + "─" * (width * (self.right - self.left) // 100))
            for y in range(1+(height * (self.bottom - self.top) // 100)):
                print(term.move(gt + (height * self.top // 100) + y, gl + width * self.left // 100) + "│")
                print(term.move(gt + (height * self.top // 100) + y, gl + width * self.right // 100) + "│")
            print(term.move(gt + (height * self.bottom // 100), gl + width * self.left // 100) + "─" * (width * (self.right - self.left) // 100))
            print(term.move(gt + height * self.top // 100, gl + width * self.left // 100) + "█")
            print(term.move(gt + height * self.top // 100, gl + width * self.right // 100) + "█")
            print(term.move(gt + (height * self.bottom // 100), gl + width * self.left // 100) + "█")
            print(term.move(gt + (height * self.bottom // 100), gl + width * self.right // 100) + "█")
            
        for child in self.children:
            child.render(
                gl + (self.left * width // 100),
                gt + (self.top * height // 100), 
                (width * (self.right - self.left) // 100), (height * (self.bottom - self.top) // 100))

main = [
    Box(20, 100, 10, 70),
    Box(20, 100, 70, 90),
    Box(0, 20, 10, 90)
]


for item in main:
    item.render(0, 0, term.width, term.height)


lx = term.width
ly = term.height

while True:
    w = term.width 
    h = term.height
    if lx != w or ly != h:
        print(term.clear)
        for item in main:
            item.render(0, 0, w, h)
        lx = w
        ly = h