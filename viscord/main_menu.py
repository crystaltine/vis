from pyfiglet import Figlet
import blessed
import random
term = blessed.Terminal()
import time

from importlib import reload

available = [
    "ogre", "pawp", "pepper", "pebbles", "puffy", "pyramid", "rectangles", "roman", "rounded", "speed", "standard", "starwars", "stellar", "thick", "tinker-toy", "univers", "barbwire", "avatar"
]

import cursor
cursor.hide()

import registry
import uuid
import json

token = registry.get_reg("token")
if token:
    import constants
    data = {
        "type": "token_bypass",
        "data": {
            "token": token,
            "uuid": uuid.getnode()
        
        }
    }
    constants.CONNECTION.sendall(json.dumps(data).encode("utf-8"))
    token = constants.CONNECTION.recv(1024).decode()
    if token == "False":
        registry.del_reg("token")
    else:
        print(token)
        exit()


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
n = time.time()
def update_screen(w, h, y):
    clear()
    print_title(Figlet(font=available[int(n) % len(available)]).renderText("Viscord"))

    update_login(w, h, y == 0)
    update_register(w, h, y == 1)
    update_quit(w, h, y == 2)

def update_login(w, h, focused):
    t = "[Log In]"
    if focused:
        print(term.move_yx(int(h * 0.5), 0) + term.clear_eol + term.move_yx(int(h * 0.5), int(w/2 - len(t)/2)) + term.black_on_lime + t + term.normal)
    else:
        print(term.move_yx(int(h * 0.5), 0) + term.clear_eol + term.move_yx(int(h * 0.5), int(w/2 - len(t)/2)) + term.white_on_black + t + term.normal)


def update_register(w, h, focused):
    t = "[Register]"
    if focused:
        print(term.move_yx(int(h * 0.5 + 1), 0) + term.clear_eol + term.move_yx(int(h * 0.5 + 1), int(w/2 - len(t)/2)) + term.black_on_lime + t + term.normal)
    else:
        print(term.move_yx(int(h * 0.5 + 1), 0) + term.clear_eol + term.move_yx(int(h * 0.5 + 1), int(w/2 - len(t)/2)) + term.white_on_black + t + term.normal)

def update_quit(w, h, focused):
    t = "[Quit]"
    if focused:
        print(term.move_yx(int(h * 0.5 + 3), 0) + term.clear_eol + term.move_yx(int(h * 0.5 + 3), int(w/2 - len(t)/2)) + term.black_on_red + t + term.normal)
    else:
        print(term.move_yx(int(h * 0.5 + 3), 0) + term.clear_eol + term.move_yx(int(h * 0.5 + 3), int(w/2 - len(t)/2)) + term.white_on_black + t + term.normal)



lw = term.width
lh = term.height

y = 0
update_screen(lw, lh, 0)

with term.cbreak():
    while True:
        w = term.width
        h = term.height
        try:
            key = term.inkey(timeout=0.01)
        except KeyboardInterrupt:
            clear()
            cursor.show()
            exit()
        if key: 
            code = key.code
            if code in [258, 512] and y < 2:
                if y == 0:
                    update_login(w, h, False)
                    update_register(w, h, True)
                if y == 1:
                    update_register(w, h, False)
                    update_quit(w, h, True)                
                y += 1
            elif code in [259, 353] and y > 0:
                if y == 1:
                    update_login(w, h, True)
                    update_register(w, h, False)
                if y == 2:
                    update_register(w, h, True)
                    update_quit(w, h, False)
                y -= 1
            elif code == 343:
                if y == 0:
                    try:
                        reload(login)
                    except:
                        import login
                    update_screen(w, h, y)
                
                elif y == 1:
                    try:
                        reload(registration)
                    except:
                        import registration
                    update_screen(w, h, y)
                elif y == 2:
                    clear()
                    cursor.show()
                    quit()
        else:
            if lw != w or lh != h:
                lw = w
                lh = h
                update_screen(w, h, y)
