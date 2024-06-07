import cursor
import sys
import registry
import config
import uuid
import server_select
import requests
import blessed
import colors
import keyshortcuts

global token
token = None

term = blessed.Terminal()

FIELD_WIDTH = int(term.width * 0.4 - 8) - 1

global selection
selection = 0

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def draw_background():
    print(term.home + term.clear, end=" ")
    for y in range(term.height):
        print(term.move(y, 0) + term.on_color_rgb(*hex_to_rgb(colors.background)) + ' ' * term.width, end="")


def draw_menu():
    tlx = int(term.width * 0.3)
    tly = int(term.height * 0.2)

    for y in range(tly, tly + int(term.height * 0.6)):
        print(term.move(y, tlx) + term.on_color_rgb(*hex_to_rgb(colors.div)) + ' ' * int(term.width * 0.4), end="")

    print(term.move(tly-1, tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.background)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + "▄" * int(term.width * 0.4 + 2), end="")
    print(term.move(tly + int(term.height * 0.6), tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.background)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + "▀" * int(term.width * 0.4 + 2), end="")
    for y in range(tly, tly + int(term.height * 0.6)):
        print(term.move(y, tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + " ", end="")
        print(term.move(y, tlx + int(term.width * 0.4)) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + " ", end="")



def center_text(text):
    return int(term.width / 2 - len(text) / 2)

def draw_all_text():
    x = center_text("New Server")
    print(term.move(int(term.height*0.35) - 2, x) + term.color_rgb(*hex_to_rgb(colors.header)) + term.on_color_rgb(*hex_to_rgb(colors.div)) + "New Server", end="")


def draw_buttons():
    global selection
    c1 = c2 = colors.button
    if selection == 0:
        c1 = colors.button_selected
    elif selection == 1:
        c2 = colors.button_selected
    
    
    x = center_text("   Create   ")
    print(term.move(int(term.height*0.5), x) + term.color_rgb(*hex_to_rgb(colors.text)) + term.on_color_rgb(*hex_to_rgb(c1)) + " " * 3 + "Create" + " " * 3, end="")
    x = center_text("    Join    ")

    print(term.move(int(term.height*0.5) + 2, x) + term.color_rgb(*hex_to_rgb(colors.text)) + term.on_color_rgb(*hex_to_rgb(c2)) + " " * 4 + "Join" + " " * 4, end="")



def redraw_all():
    print(term.clear)
    draw_background()
    draw_menu()
    draw_all_text()
    draw_buttons()
    print(term.normal, flush=True)


    

def main(user_token):
    global token, selection
    token = user_token
    redraw_all()

    with term.cbreak():
        val = ""
        while True:
            sx = term.width
            sy = term.height
            val = term.inkey(timeout=0.01)
            if not val:
                if term.width != sx or term.height != sy:
                    redraw_all()
                continue
            
            if val.code == term.KEY_ESCAPE:
                return None

            if val.code == term.KEY_ENTER:
                if selection == 0:
                    import create_server
                    ret = create_server.main(token)
                    if ret:
                        return ret
                    else:
                        return None
                elif selection == 1:
                    import join_server
                    ret = join_server.main(token)
                    if ret:
                        return ret
                    else:
                        return None
                redraw_all()
                continue
            if repr(val) in keyshortcuts.back_keys:
                selection = max(0, selection - 1)
                draw_buttons()
                print("")
            elif repr(val) in keyshortcuts.next_keys:
                selection = min(1, selection + 1)
                draw_buttons()
                print("")
            
            

if __name__ == "__main__":
    main()