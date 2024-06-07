import uuid
import blessed
term = blessed.Terminal()
import colors
import cursor
import keyshortcuts
import requests
import config
import registry
import sys
import random

global code
code = ""

FIELD_WIDTH = int(term.width * 0.4 - 8) - 1

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
    global server, code
    x = center_text("Invite Creation")
    print(term.move(int(term.height*0.35) - 2, x) + term.on_color_rgb(*hex_to_rgb(colors.div)) + term.color_rgb(*hex_to_rgb(colors.header)) + "Select a Channel", end="")

    if code:
        display_success(f"Invite code: {code}")
    else:
        display_error("Could not create invite code")

    

def draw_fields():
    global data, selection
    length = int(term.height * 0.6) - int(term.height*0.35)

def redraw_all():
    print(term.clear())
    draw_background()
    draw_menu()
    draw_all_text()
    draw_fields() 
    print("")

def display_error(msg):
    if not msg:
        print(term.move(int(term.height*0.5) + 2, int(term.width * 0.3)) + term.on_color_rgb(*hex_to_rgb(colors.div)) + " " * int(term.width * 0.4), end="")
    else:
        print(term.move(int(term.height*0.5) + 2, center_text(msg)) + term.color_rgb(*hex_to_rgb(colors.error)) + term.on_color_rgb(*hex_to_rgb(colors.div)) + msg, end="")

def display_success(msg):
    display_error(None)
    if not msg:
        print(term.move(int(term.height*0.5) + 2, int(term.width * 0.3)) + term.on_color_rgb(*hex_to_rgb(colors.div)) + " " * int(term.width * 0.4), end="")
    else:
        print(term.move(int(term.height*0.5) + 2, center_text(msg)) + term.color_rgb(*hex_to_rgb(colors.success)) + term.on_color_rgb(*hex_to_rgb(colors.div)) + msg, end="", flush=True)
        sys.stdout.flush()


def main(token, server_id):
    global code
    resp = requests.post(f"{config.API_URL}/api/invites/create", json={
        "user_token": token,
        "server_id": server_id
    })
    if resp.status_code != 200:
        display_error("Could not create invite")
        
    else:
        code = resp.json()["invite_code"]
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
            if val.code == term.KEY_ESCAPE or val.code == term.KEY_ENTER:
                break        