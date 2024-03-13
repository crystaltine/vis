from pyfiglet import Figlet
import blessed
import random
term = blessed.Terminal()

def clear():
    print(term.clear)

def print_title(title):
    lines = title.split("\n")
    w, h = term.width, term.height
    clear()
    for i, line in enumerate(lines):
        print(
            term.move_yx(i, (w // 2) - (len(line) // 2)) + line
        )

available = [
    "ogre", "pawp", "pepper", "pebbles", "puffy", "pyramid", "rectangles", "roman", "rounded", "speed", "standard", "starwars", "stellar", "thick", "tinker-toy", "univers", "barbwire", "avatar"
]

import time
for f in available:
    x = Figlet(font=f).renderText("Viscord")
    clear()
    print_title(x)
    time.sleep(1)