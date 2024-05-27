import uuid
import blessed
term = blessed.Terminal()
import COLORS
import cursor
import keyshortcuts
import requests
import config
import registry
import sys
import random

global selection
selection = 0
selected = None

global cursor_pos
cursor_pos = 0

global username, password
username = ""
password = ""

global error_show
error_show = False

global data
data = []

FIELD_WIDTH = int(term.width * 0.4 - 8) - 1

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def draw_background():
    print(term.home + term.clear, end=" ")
    for y in range(term.height):
        print(term.move(y, 0) + term.on_color_rgb(*hex_to_rgb(COLORS.background)) + ' ' * term.width, end="")


def draw_menu():
    tlx = int(term.width * 0.3)
    tly = int(term.height * 0.2)

    for y in range(tly, tly + int(term.height * 0.6)):
        print(term.move(y, tlx) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + ' ' * int(term.width * 0.4), end="")


def center_text(text):
    return int(term.width / 2 - len(text) / 2)

def draw_all_text():
    x = center_text("Select a Server")
    print(term.move(int(term.height*0.35) - 2, x) + term.color_rgb(*hex_to_rgb(COLORS.header)) + "Select a Server", end="")

    

def draw_fields():
    global data, selection
    length = int(term.height * 0.6) - int(term.height*0.35)
    if selection < length:
        chunk = data[:length]
    else:
        chunk = data[max(selection-length+1, 1):selection]
    field_length = int(term.width * 0.2) + 1
    cursor_pos = selection
    for i, server in enumerate(chunk):
        name = "(" + server["server_icon"] + ") " + server["server_name"]
        if len(name) > field_length:
            name = name[:field_length-3] + "..."
        if i == cursor_pos:
            print(term.move_yx(int(term.height*0.35) + i, int(term.width * 0.4)) + term.on_color_rgb(*hex_to_rgb(COLORS.field_highlighted)) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.bold(name + " " * (field_length - len(name))), end="", flush=True)
        else:
            print(term.move_yx(int(term.height*0.35) + i, int(term.width * 0.4)) + term.color_rgb(*hex_to_rgb(server["color"])) + term.on_color_rgb(*hex_to_rgb(COLORS.field)) + term.bold(name + " " * (field_length - len(name))), end="", flush=True)



def redraw_all():
    print(term.clear())
    draw_background()
    draw_menu()
    draw_all_text()
    draw_fields() 

def main(user_token):
    global data, selection
    resp = requests.post(config.API_URL + "/api/members/all_servers", json={"user_token": user_token})
    server_ids = resp.json()["data"]
    data = []
    for server_id in server_ids:
        resp = requests.post(config.API_URL + "/api/servers/server_info", json={"server_id": server_id, "user_token": user_token})
        returned = resp.json()["data"]
        returned["server_id"] = server_id
        data.append(returned)

    
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
                print(term.clear + term.normal)
                cursor.show()
                sys.exit(0)
            if val.code == term.KEY_DOWN:
                selection += 1
                if selection >= len(data):
                    selection = len(data) - 1
                draw_fields()
            if val.code == term.KEY_UP:
                selection -= 1
                if selection < 0:
                    selection = 0
                draw_fields()
            if val.code == term.KEY_ENTER:
                import channel_select
                print(data[selection])
                channel_select.main(data[selection], user_token)
