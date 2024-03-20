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


s.setblocking(False)


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

input_volume = 200 # range from 0 to 200
output_volume = 100

dbfs_threshold = -50

def handle_voice_io():
    while True:
        data = input_stream.read(CHUNK)
        restructured = pydub.AudioSegment(data, sample_width=2, channels=1, frame_rate=RATE)
        if data:
            #print(restructured.dBFS)
            if restructured.dBFS > dbfs_threshold:
                restructured = restructured.apply_gain(pydub.utils.ratio_to_db(input_volume / 100))
                s.sendall(restructured.raw_data)
        try:
            resp = s.recv(2048)
        except BlockingIOError:
            continue
        if resp:
            output_stream.write(resp)

import threading
threading.Thread(target=handle_voice_io).start()