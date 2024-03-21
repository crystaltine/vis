import pyaudio
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100  # Sample rate (samples per second)
CHUNK = 1024  # Number of frames per buffer

import io
import numpy as np
import pydub
import json

# Initialize PyAudio
audio = pyaudio.PyAudio()

import socket

outgoing_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
outgoing_socket.connect(("trigtbh.dev", 5000))
outgoing_socket.sendall(json.dumps({"type": "outgoing-voice", "channel_id": "test"}).encode("utf-8"))
outgoing_socket.recv(2048)

incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
incoming_socket.connect(("trigtbh.dev", 5000))
incoming_socket.sendall(json.dumps({"type": "incoming-voice", "channel_id": "test"}).encode("utf-8"))
incoming_socket.recv(2048)

print("Outgoing, incoming up!")

global input_stream, output_stream

input_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

output_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True)

input_volume = 200 # range from 0 to 200
output_volume = 100

import time
def ping_thread():
    while True:
        x = time.time()
        outgoing_socket.sendall(json.dumps({"type": "ping"}).encode("utf-8"))
        incoming_socket.sendall(json.dumps({"type": "ping"}).encode("utf-8"))
        outgoing_socket.recv(2048)
        incoming_socket.recv(2048)
        print(time.time() - x * 1000)

def outgoing_thread():
    global input_stream
    while True:
        try:
            data = input_stream.read(CHUNK)
        except OSError as e:
            try:
                input_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
            except:
                raise e
            else:
                continue
        restructured = pydub.AudioSegment(data, sample_width=2, channels=1, frame_rate=RATE)

        if data:
            restructured = restructured.apply_gain(pydub.utils.ratio_to_db(input_volume / 100))
            outgoing_socket.sendall(restructured.raw_data)
            

def incoming_thread():
    global output_stream
    while True:
        try:
            data = incoming_socket.recv(CHUNK)
        except BlockingIOError:
            continue
        if data:
            try:
                output_stream.write(data)
            except OSError as e:
                try:
                    output_stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True)
                except:
                    raise e
                else:
                    continue

import threading
threading.Thread(target=outgoing_thread).start()
threading.Thread(target=incoming_thread).start()