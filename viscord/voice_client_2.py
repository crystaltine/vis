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

input_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

output_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True)

def outgoing_thread():
    while True:
        data = input_stream.read(CHUNK)
        restructured = pydub.AudioSegment(data, sample_width=2, channels=1, frame_rate=RATE)
        if data:
            outgoing_socket.sendall(restructured.raw_data)
    
def incoming_thread():
    while True:
        data = incoming_socket.recv(2048)
        if data:
            output_stream.write(data)

import threading
threading.Thread(target=outgoing_thread).start()
threading.Thread(target=incoming_thread).start()
