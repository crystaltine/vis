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

global update_direction
update_direction = 0

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

global data, server
data = []
server = {}

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
    global server
    x = center_text("Select a Channel")
    print(term.move(int(term.height*0.35) - 2, x) + term.on_color_rgb(*hex_to_rgb(colors.div)) + term.color_rgb(*hex_to_rgb(colors.header)) + "Select a Channel", end="")
    server_display = f"({server['server_icon']}) {server['server_name']}"
    x = center_text(server_display)
    print(term.move(int(term.height*0.35) - 4, x) + term.color_rgb(*hex_to_rgb(server["color"])) + server_display, end="")

    

def draw_fields():
    global data, selection
    length = int(term.height * 0.6) - int(term.height*0.35)


    chunks = [data[i:i+length] for i in range(0, len(data), length)]
    if not chunks:
        return
    
    chunk = chunks[selection // length]
    cursor_pos = selection % length
    field_length = int(term.width * 0.2) + 1

    if len(chunks) > 1 and selection // length != len(chunks) - 1:
        x = center_text("vvv")
        print(term.move(int(term.height*0.35) + length, x) + term.on_color_rgb(*hex_to_rgb(colors.div)) + term.cyan + "vvv", end="")
    else:
        x = center_text("vvv")
        print(term.move(int(term.height*0.35) + length, x) + term.on_color_rgb(*hex_to_rgb(colors.div)) + "   ", end="")
    if len(chunks) > 1 and selection // length != 0:
        x = center_text("^^^")
        print(term.move(int(term.height*0.35) - 1, x) + term.on_color_rgb(*hex_to_rgb(colors.div)) + term.cyan + "^^^", end="")
    else:
        x = center_text("^^^")
        print(term.move(int(term.height*0.35) - 1, x) + term.on_color_rgb(*hex_to_rgb(colors.div)) + "   ", end="")

    for i in range(length):
        if i >= len(chunk):
            print(term.move_yx(int(term.height*0.35) + i, int(term.width * 0.4)) + term.on_color_rgb(*hex_to_rgb(colors.div)) + term.color_rgb(*hex_to_rgb(colors.text)) + " " * field_length, end="", flush=True)
            continue
        chat = chunk[i]
        name = chat["chat_name"]
        if len(name) > field_length:
            name = name[:field_length-3] + "..."
        if i == cursor_pos:
            print(term.move_yx(int(term.height*0.35) + i, int(term.width * 0.4)) + term.on_color_rgb(*hex_to_rgb(colors.field_highlighted)) + term.color_rgb(*hex_to_rgb(colors.text)) + term.bold(name + " " * (field_length - len(name))), end="", flush=True)
        else:
            print(term.move_yx(int(term.height*0.35) + i, int(term.width * 0.4)) + term.color_rgb(*hex_to_rgb(colors.unselected_text)) + term.on_color_rgb(*hex_to_rgb(colors.field)) + term.bold(name + " " * (field_length - len(name))), end="", flush=True)

def redraw_all():
    print(term.clear())
    draw_background()
    draw_menu()
    draw_all_text()
    draw_fields() 
    print("")

def main(server_data, user_token):
    global data, selection, server

    # get all channels that are visible
    data = []
    server = server_data
    resp = requests.post(config.API_URL + "/api/servers/get_chats", json={"user_token": user_token, "server_id": server_data["server_id"]})
    
    for channel in resp.json()["data"]:
        data.append(channel)

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
                break
            if val.code == term.KEY_DOWN:
                selection += 1
                if selection >= len(data):
                    selection = len(data) - 1
                update_direction = 1
                draw_fields()
            if val.code == term.KEY_UP:
                selection -= 1
                if selection < 0:
                    selection = 0
                update_direction = -1
                draw_fields()
            if val.code == term.KEY_ENTER:
                if selection >= len(data):
                    continue
                channel = data[selection]
                import messages
                messages.main(user_token, server["server_id"], channel["chat_id"])
                redraw_all()

            if val == "\x04": # control-d
                import create_invite
                create_invite.main(user_token, server["server_id"])
                redraw_all()
            elif val == "\x0b":
                import voice_client
                voice_client.main(user_token, server["server_id"], data[selection]["chat_id"])
                redraw_all()