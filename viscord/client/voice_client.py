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
from global_functions import *
import socket
import json
import pyaudio
import threading

global selection
selection = 0
selected = None

global cursor_pos
cursor_pos = 0

global error_show
error_show = False

global token, server, channel
token = server = channel = None

FIELD_WIDTH = int(term.width * 0.4 - 8) - 1

FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100  # Sample rate (samples per second)
CHUNK = 1024  # Number of frames per buffer

global transmitting
transmitting = True

audio = pyaudio.PyAudio()

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


    # draw a border
    print(term.move(tly-1, tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.background)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + "▄" * int(term.width * 0.4 + 2), end="")
    print(term.move(tly + int(term.height * 0.6), tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.background)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + "▀" * int(term.width * 0.4 + 2), end="")
    for y in range(tly, tly + int(term.height * 0.6)):
        print(term.move(y, tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + " ", end="")
        print(term.move(y, tlx + int(term.width * 0.4)) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + " ", end="")


def center_text(text):
    return int(term.width / 2 - len(text) / 2)

def draw_all_text():
    x = center_text("In Voice")
    print(term.move(int(term.height*0.35) - 2, x) + term.color_rgb(*hex_to_rgb(colors.header)) + term.on_color_rgb(*hex_to_rgb(colors.div)) + "In Voice", end="")


def create_lifeline(user_id, chat_id):
    global transmitting
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config.HOST, config.VOICE_PORT))
    s.sendall(json.dumps({
        "role": "lifeline",
        "id": user_id,
    }).encode())

    while transmitting:
        data = s.recv(2048)
        if not data:
            break
        try:
            data = json.loads(data.decode())
            if data["msg"] == "join":
                threading.Thread(target=create_listener, args=(user_id, data["id"], chat_id)).start()
        except:
            pass

    s.close()

def create_sender(user_id, channel):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config.HOST, config.VOICE_PORT))
    s.sendall(json.dumps({
        "role": "sender",
        "id": user_id,
        "chat_id": channel
        }).encode())
    input_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while transmitting:
        try:
            data = input_stream.read(CHUNK)
            if data:
                s.sendall(data)
        except:
            break
    s.close()


def create_listener(user_id, target, chat_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config.HOST, config.VOICE_PORT))
    s.sendall(json.dumps({
        "role": "receiver",
        "id": user_id,
        "chat_id": chat_id,
        "target": target
    }).encode())

    output_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)

    while True:
        try:
            data = s.recv(2048)
        except:
            s.close()
            break
        if data:
            output_stream.write(data)

def redraw_all():
    print(term.clear())
    draw_background()
    draw_menu()
    draw_all_text()
    print("")


def main(user_token, server_id, channel_id):
    global token, server, channel, transmitting
    token = user_token
    server = server_id
    channel = channel_id

    user_info = requests.post(f"https://{config.HOST}:{config.PORT}/api/users/whoami", json={"user_token": user_token})
    if user_info.status_code != 200:
        return None
    user_id = user_info.json()["user_id"]
    
    
    try:
        resp = requests.post(f"https://{config.HOST}:{config.PORT}/api/voice/join", json={"user_token": user_token, "server_id": server_id, "chat_id": channel_id})
    except Exception as e:
        return None
    
    if resp.status_code != 200:
        return None
    
    


    callbacks = resp.json()["connections"]
    for target in callbacks:
        if target == "lifeline":
            threading.Thread(target=create_lifeline, args=(user_id, channel_id)).start()
        else:
            threading.Thread(target=create_listener, args=(user_id, target, channel_id)).start()


    
    threading.Thread(target=create_sender, args=(user_id, channel_id)).start()


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
                transmitting = False
                break