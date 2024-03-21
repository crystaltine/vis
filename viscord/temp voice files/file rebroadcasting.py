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


def run_stuff(file_path, file_path2):
    import pydub
    audio = pydub.AudioSegment.from_file(file_path, sample_width=2, channels=1, frame_rate=RATE)
    audio_2 = pydub.AudioSegment.from_file(file_path2, sample_width=2, channels=1, frame_rate=RATE)
    # loop through chunks of frames in both audios, or one if one is shorter
    print(len(audio.raw_data), len(audio_2.raw_data))
    for i in range(min(len(audio.raw_data), len(audio_2.raw_data))//CHUNK):
        print("x")
        # get the current chunk of frames from both audios
        chunk = np.frombuffer(audio.raw_data[i*CHUNK*2:(i+1)*CHUNK*2], dtype=np.int16)
        chunk_2 = np.frombuffer(audio_2.raw_data[i*CHUNK*2:(i+1)*CHUNK*2], dtype=np.int16)
        # add the frames together
        chunk = (chunk + chunk_2)
        # convert the frames back to bytes
        chunk = chunk.astype(np.int16).tobytes()
        # play the chunk
        output_stream.write(chunk)

    print("Done!")

#run_stuff("C:/Users/ms_lu/Downloads/panacea.mp3")
import threading

audio = pydub.AudioSegment.from_file("C:/Users/ms_lu/Downloads/panacea.mp3", sample_width=2, channels=1, frame_rate=RATE)
print("A")
#audio = pydub.effects.speedup(audio, playback_speed=2.0)
raw_data = audio.raw_data
print(audio.frame_rate)
import time
for i in range(0, len(raw_data), CHUNK*2):
    data = raw_data[i:i+CHUNK*2]
    array = np.frombuffer(data, dtype=np.int16)
    # add one element to the array 
    np.append(array, 0)
    # convert the array back to bytes
    data = array.astype(np.int16).tobytes()
    print(len())
