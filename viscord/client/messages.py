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
import json
import multiprocessing as mp

import socket

global s
s = None

global data
data = {}

global typed_message
typed_message = ""

def draw_typed_message():
    print(term.move(int(term.height * 0.9 - 2), int(term.width * 0.1) + 1) + term.on_color_rgb(*hex_to_rgb(colors.field)) + term.color_rgb(*hex_to_rgb(colors.text)) + " " * (int(term.width * 0.8 - 2)))

    print(term.move(int(term.height * 0.9 - 4), int(term.width * 0.1)) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + " " * (int(term.width * 0.8)))

    


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def draw_background():
    print(term.home + term.clear, end=" ")
    for y in range(term.height):
        print(term.move(y, 0) + term.on_color_rgb(*hex_to_rgb(colors.background)) + ' ' * term.width, end="")


def draw_menu():
    tlx = int(term.width * 0.1)
    tly = int(term.height * 0.1)

    for y in range(tly, tly + int(term.height * 0.8)):
        print(term.move(y, tlx) + term.on_color_rgb(*hex_to_rgb(colors.div)) + ' ' * int(term.width * 0.8), end="")

    print(term.move(tly-1, tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.background)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + "▄" * int(term.width * 0.8 + 2), end="")
    print(term.move(tly + int(term.height * 0.8), tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.background)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + "▀" * int(term.width * 0.8 + 2), end="")
    for y in range(tly, tly + int(term.height * 0.8)):
        print(term.move(y, tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + " ", end="")
        print(term.move(y, tlx + int(term.width * 0.8)) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + " ", end="")

def socket_handler():
    global s, data
    try:
        while True:
            data = s.recv(4096)
            if not data:
                break
            message_data = json.loads(data.decode())
            data.append(message_data)
            show_recent_messages()
    except Exception as e:
        pass
    

def show_recent_messages():
    tly = int(term.height * 0.1)
    tlx = int(term.width * 0.1)

    for y in range(tly, tly + int(term.height * 0.8) - 4):
        print(term.move(y, tlx) + term.on_color_rgb(*hex_to_rgb(colors.div)) + " " * (int(term.width * 0.8)))


def redraw_all():
    draw_background()
    draw_menu()

    draw_typed_message()
    show_recent_messages()

    print("")



def main(user_token, server_id, channel_id):
    global s, data
    import traceback
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s.connect((config.HOST, config.SOCKET_PORT))
        s.send(user_token.encode())


        resp = requests.post(f"{config.API_URL}/api/messages/get_recent", json={
            "chat_id": channel_id,
            "server_id": server_id,
            "user_token": user_token,
            "num": 15
        })
        if resp.status_code != 200:
            return
        data = resp.json()["data"]
    except Exception as e:
        return

    proc = mp.Process(target=socket_handler)
    proc.start()

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
                s.close()
                proc.terminate()
                break
            