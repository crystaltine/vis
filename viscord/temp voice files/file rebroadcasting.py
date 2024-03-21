import pyaudio
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100*2  # Sample rate (samples per second)
CHUNK = 1024  # Number of frames per buffer

import io
import numpy as np
import pydub
import json

# Initialize PyAudio
audio = pyaudio.PyAudio()

import socket

# outgoing_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# outgoing_socket.connect(("trigtbh.dev", 5000))
# outgoing_socket.sendall(json.dumps({"type": "outgoing-voice", "channel_id": "test"}).encode("utf-8"))
# outgoing_socket.recv(2048)


output_stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True)

print("Outgoing up!")


file_path = "C:/Users/ms_lu/Downloads/panacea.mp3"
import pydub
audio = pydub.AudioSegment.from_file(file_path, sample_width=2, channels=1, frame_rate=RATE)
raw_data = audio.raw_data
for i in range(0, len(raw_data), CHUNK*2):
    output_stream.write(raw_data[i:i+CHUNK*2])