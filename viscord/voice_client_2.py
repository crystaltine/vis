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
outgoing_socket.setblocking(False)

incoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
incoming_socket.connect(("trigtbh.dev", 5000))
incoming_socket.sendall(json.dumps({"type": "incoming-voice", "channel_id": "test"}).encode("utf-8"))
incoming_socket.recv(2048)
incoming_socket.setblocking(False)

print("Outgoing, incoming up!")

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

dbfs_threshold = -50

import time
def send_data(data):
    time.sleep(0.1)
    outgoing_socket.sendall(data)

def outgoing_thread():
    clength = 0
    while True:
        data = input_stream.read(CHUNK)
        restructured = pydub.AudioSegment(data, sample_width=2, channels=1, frame_rate=RATE)
        #
        if data:
            if restructured.dBFS > dbfs_threshold:
                clength += 1
                print(restructured.dBFS)
                restructured = restructured.apply_gain(pydub.utils.ratio_to_db(input_volume / 100))
                threading.Thread(target=send_data, args=(restructured.raw_data,)).start()
            else:
                if clength > 0:
                    print("clength:", clength)
                clength = 0

def incoming_thread():
    rlength = 0
    while True:
        try:
            data = incoming_socket.recv(CHUNK)
        except BlockingIOError:
            if rlength > 0:
                print("rlength:", rlength)
            rlength = 0
            continue
        if data:
            rlength += 1
            output_stream.write(data)

import threading
threading.Thread(target=outgoing_thread).start()
threading.Thread(target=incoming_thread).start()
