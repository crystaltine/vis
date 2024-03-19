import pyaudio
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100  # Sample rate (samples per second)
CHUNK = 1024  # Number of frames per buffer

import io
import numpy as np
import pydub

# Initialize PyAudio
audio = pyaudio.PyAudio()

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("trigtbh.dev", 5000))
print("up!")

input_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

output_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True)


def handle_voice_io():
    while True:
        data = input_stream.read(CHUNK)
        if data:
            # restructured = pydub.AudioSegment(data, sample_width=2, channels=1, frame_rate=RATE) + 10
            # export = io.BytesIO()
            s.sendall(data)
        resp = s.recv(2048)
        if resp:
            output_stream.write(resp)


import threading
threading.Thread(target=handle_voice_io).start()