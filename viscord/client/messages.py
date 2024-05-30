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
import threading

global getting_messages
getting_messages = True

import socket

global token
token = None

global s
s = None

global data
data = {}

global typed_message
typed_message = ""

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


def draw_typed_message():
    global typed_message
    #print(term.move(int(term.height * 0.9 - 2), int(term.width * 0.1) + 1) + term.on_color_rgb(*hex_to_rgb(colors.field)) + term.color_rgb(*hex_to_rgb(colors.text)) + " " * (int(term.width * 0.8 - 2)))

    print(term.move(int(term.height * 0.9 - 4), int(term.width * 0.1)) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + " " * (int(term.width * 0.8)))


    chunked = [typed_message[i:i+int(term.width * 0.8 - 2) - 1] for i in range(0, len(typed_message), int(term.width * 0.8 - 2) - 1)]
    try:
        if len(chunked) > 0:
            to_show = chunked[-1]
            print(term.move(int(term.height * 0.9 - 2), int(term.width * 0.1) + 1) + term.on_color_rgb(*hex_to_rgb(colors.field)) + term.color_rgb(*hex_to_rgb(colors.text)) + to_show + " " * (int(term.width * 0.8 - 2) - len(to_show)))
            if len(chunked) > 1:
                print(term.move(int(term.height * 0.9 - 2), int(term.width * 0.1)) + term.cyan + term.on_color_rgb(*hex_to_rgb(colors.div)) + "<" + term.normal)
            else:
                print(term.move(int(term.height * 0.9 - 2), int(term.width * 0.1)) + term.cyan + term.on_color_rgb(*hex_to_rgb(colors.div)) + " " + term.normal)
            print(term.move(int(term.height * 0.9 - 2), int(term.width * 0.1) + 1 + len(to_show)) + term.on_color_rgb(*hex_to_rgb(colors.cursor)) + term.color_rgb(*hex_to_rgb(colors.text)) + " ")
        else:
            print(term.move(int(term.height * 0.9 - 2), int(term.width * 0.1) + 1) + term.on_color_rgb(*hex_to_rgb(colors.field)) + term.color_rgb(*hex_to_rgb(colors.text)) + " " * (int(term.width * 0.8 - 2)))
            print(term.move(int(term.height * 0.9 - 2), int(term.width * 0.1) + 1) + term.on_color_rgb(*hex_to_rgb(colors.cursor)) + term.color_rgb(*hex_to_rgb(colors.text)) + " ")
        
    except Exception as e:
        print(str(e))


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
    global s, data, getting_messages, token
    while not s:
        pass
    try:
        while getting_messages:
            receiveddata = s.recv(4096)
            if not receiveddata:
                break
            message_data = json.loads(receiveddata.decode())

            msgdata_real = message_data["data"]
            user_id = msgdata_real["author"]
            resp = requests.post(f"{config.API_URL}/api/users/user_info", json={
                "user_id": user_id,
                "user_token": token
            })

            msgdata_real["username"] = resp.json()["data"]["username"]
            msgdata_real["color"] = resp.json()["data"]["color"]
            msgdata_real["symbol"] = resp.json()["data"]["symbol"]

            data.insert(0, message_data["data"])
            show_recent_messages()
    except Exception as e:
        print(e)
    

def show_recent_messages():
    tly = int(term.height * 0.1)
    tlx = int(term.width * 0.1)

    for y in range(tly, tly + int(term.height * 0.8) - 4):
        print(term.move(y, tlx) + term.on_color_rgb(*hex_to_rgb(colors.div)) + " " * (int(term.width * 0.8)))

    starting_y = tly + int(term.height * 0.8) - 5
    msg_index = 0
    while starting_y > tly:
        if msg_index >= len(data):
            break
        msg = data[msg_index]
        msg_index += 1
        text = msg["message_content"]


        chunks = [text[i:i+int(term.width * 0.8 - 2) - 1] for i in range(0, len(text), int(term.width * 0.8 - 2) - 1)]

        for chunk in chunks[::-1]:
            print(term.move(starting_y, tlx) + term.on_color_rgb(*hex_to_rgb(colors.div)) + term.color_rgb(*hex_to_rgb(colors.text)) + chunk + " " * (int(term.width * 0.8 - len(chunk))))
            starting_y -= 1
            if starting_y == tly:
                break

        if starting_y <= tly:
            break
        

        if msg_index < len(data) - 1 and data[msg_index]["author"] == msg["author"]:
            continue
        color = msg["color"]
        symbol = msg["symbol"]
        username = msg["username"]
        print(term.move(starting_y, tlx) + term.on_color_rgb(*hex_to_rgb(colors.div)) + term.color_rgb(*hex_to_rgb(color)) + term.bold + f"{symbol} {username}" + term.normal, end="", flush=True)
        starting_y -= 2

        


def redraw_all():
    draw_background()
    draw_menu()

    draw_typed_message()
    show_recent_messages()

    print("")



def main(user_token, server_id, channel_id):
    global s, data, getting_messages, typed_message, token
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

        for i in range(len(data)):
            user_id = data[i]["user_id"]
            data[i]["author"] = user_id

            resp = requests.post(f"{config.API_URL}/api/users/user_info", json={
                "user_id": user_id,
                "user_token": user_token
            })

            data[i]["username"] = resp.json()["data"]["username"]
            data[i]["color"] = resp.json()["data"]["color"]
            data[i]["symbol"] = resp.json()["data"]["symbol"]

    except Exception as e:
        return

    threading.Thread(target=socket_handler).start()

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
                getting_messages = False
                typed_message = ""
                break
            elif val.code is None and val in keyshortcuts.typeable:
                typed_message += val
                draw_typed_message()
            elif val.code == term.KEY_BACKSPACE:
                typed_message = typed_message[:-1]
                draw_typed_message()
            elif val.code == term.KEY_ENTER:
                resp = requests.post(f"{config.API_URL}/api/messages/send", json={
                    "chat_id": channel_id,
                    "server_id": server_id,
                    "user_token": user_token,
                    "message_content": typed_message,
                    "pinged_user_ids": [], # TODO: figure out,
                    "replied_to_id": None
                })
                if resp.status_code != 200:
                    continue

                socket_data = {
                    "token": user_token,
                    "message_id": resp.json()["data"]["message_id"]
                }
                s.send(json.dumps(socket_data).encode())

                typed_message = ""
                draw_typed_message()

