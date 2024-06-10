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
import cv2
from PIL import Image


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


width = 90
height = 50

def split_large(n):
    byte1 = n & 0xFF
    byte2 = n >> 8
    return byte1, byte2

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def draw_background():
    print(term.home + term.clear, end=" ")
    for y in range(term.height):
        print(term.move(y, 0) + term.on_color_rgb(*hex_to_rgb(colors.background)) + ' ' * term.width, end="")


def encode_video(int_array):
    byte_array = []
    for num in int_array:
        byte_array.append((num >> 8) & 0xFF)  
        byte_array.append(num & 0xFF)         
    return byte_array


def decode_video(byte_array):
    ints = []
    for i in range(0, len(byte_array), 2):
        ints.append((byte_array[i] << 8) | byte_array[i+1])
    return ints

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
        "chat_id": chat_id
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
    global transmitting
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
            else:
                break
        except:
            break
    s.close()


def create_listener(user_id, target, chat_id):
    global transmitting
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

    while transmitting:
        try:
            data = s.recv(2048)
        except:
            s.close()
            break
        if data:
            output_stream.write(data)
        else:
            break
    s.close()

def create_video_lifeline(user_id, chat_id):
    global transmitting
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config.HOST, config.VIDEO_PORT))
    s.sendall(json.dumps({
        "role": "lifeline",
        "id": user_id,
        "chat_id": chat_id
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

def create_video_sender(user_id, channel):
    global transmitting
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config.HOST, config.VIDEO_PORT))
    s.sendall(json.dumps({
        "role": "sender",
        "id": user_id,
        "chat_id": channel
        }).encode())
    
    
    vidcap = cv2.VideoCapture(0)

    while transmitting:
        try:
            success, image = vidcap.read()
            if not success:
                break
            # s.sendall(data)
            # TODO
            im = Image.fromarray(image)
            im = im.resize((width, height))


            pixels = im.load()
            pixels = [[pixels[x, y] for x in range(width)] for y in range(height)]
            pixels = [[
                (r // 16, g // 16, b // 16)
                for r, g, b in row
            ] for row in pixels]

            pixels = [
                r << 8 | g << 4 | b
                for row in pixels
                for r, g, b in row
            ]

            
            temp = bytes(encode_video(pixels))
            print(f"sending: {len(temp)} bytes")
            s.sendall(temp)

        except:
            break
    s.close()
    vidcap.release()


def create_video_listener(user_id, target, chat_id):
    global transmitting
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.HOST, config.VIDEO_PORT))
    s.sendall(json.dumps({
        "role": "receiver",
        "id": user_id,
        "chat_id": chat_id,
        "target": target
    }).encode())

    while transmitting:
        try:
            data = s.recv(9000)
        except:
            s.close()
            break
        if data:
            video_data = decode_video(data)
            print(len(video_data))

            printed = term.move_yx((term.height - height) // 2, (term.width - width) // 2)

            for y in range(0, height, 2):
                for x in range(width):
                    
                    p1 = video_data[y * width + x]
                    p2 = video_data[(y + 1) * width + x]

                    b1 = p1 >> 8
                    g1 = (p1 >> 4) & 0xf
                    r1 = p1 & 0xf

                    b2 = p2 >> 8
                    g2 = (p2 >> 4) & 0xf
                    r2 = p2 & 0xf




                    char = "▀"
                    printed = printed + (term.on_color_rgb(r2 * 16, g2 * 16, b2 * 16) + term.color_rgb(r1 * 16, g1 * 16, b1 * 16) + char + term.normal)
                printed = printed + term.move_yx((term.height - height + y) // 2, (term.width - width) // 2)
            print(printed, end="", flush=True)


        else:
            break
    s.close()


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

    # VOICE CONNECTIONS
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



    # VIDEO CONNECTIONS
    try:
        resp = requests.post(f"https://{config.HOST}:{config.PORT}/api/video/join", json={"user_token": user_token, "server_id": server_id, "chat_id": channel_id})
    except Exception as e:
        return None
    
    if resp.status_code != 200:
        return None

    callbacks = resp.json()["connections"]
    for target in callbacks:
        if target == "lifeline":
            threading.Thread(target=create_video_lifeline, args=(user_id, channel_id)).start()
        else:
            threading.Thread(target=create_video_listener, args=(user_id, target, channel_id)).start()

    threading.Thread(target=create_video_sender, args=(user_id, channel_id)).start()



    redraw_all()
    
    with term.cbreak():
        val = ""
        while True:
            sx = term.width
            sy = term.height
            val = term.inkey(timeout=0.01)
            if not val:
                if term.width != sx or term.height != sy:
                    pass
                    redraw_all()
                continue
            if val.code == term.KEY_ESCAPE:
                transmitting = False
                break