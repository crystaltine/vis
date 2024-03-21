import socket
import threading
import json

from uuid import uuid4
import random
import datetime

import numpy as np
import time
 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5000))

print("Server up!")
print("Running on " + str(s.getsockname()[0]) + ":" + str(s.getsockname()[1]))


connections = {}

incoming_connections = {}
outgoing_connections = {}

data_queues = {}

import queue

no_voice_echo = False

def rebroadcast_voice():
    while True:
        for conn, addr in data_queues:
            target = time.time()
            data = data_queues[(conn, addr)]
            if len(data) == 0:
                continue
            if len(data) == 1:
                conn.sendall(data[0])
                data_queues[(conn, addr)] = []
            else:
                a = data[0]
                b = data[1]
                addition = np.frombuffer(b[0], dtype=np.int16)
                addition = np.pad(addition, (0, 1024 - len(addition)))
                full_data = np.frombuffer(a[0], dtype=np.int16)
                full_data = np.pad(full_data, (0, 1024 - len(full_data)))
                full_data += addition

                i = 2
                while i < len(data) and data[i][1] < target:
                    addition = np.frombuffer(data[i][0], dtype=np.int16)
                    addition = np.pad(addition, (0, 1024 - len(addition)))
                    full_data += addition
                    i += 1
                full_data = full_data.astype(np.int16).tobytes()
                conn.sendall(full_data)
                data_queues[(conn, addr)] = []
                

def handle_voice(conn, addr, data):
    channel_id = incoming_connections.get(addr)
    if channel_id:
        for conn2, addr2 in outgoing_connections[channel_id]:
            if (no_voice_echo and addr[0] != addr2) or not no_voice_echo:
                data_queues[(conn2, addr2)].append((data, time.time()))

def handle_outgoing_voice(conn, addr, data): # outgoing FROM THE CLIENT PERSPECTIVE
    if conn not in incoming_connections:
        incoming_connections[addr] = data["channel_id"]
    if data["channel_id"] not in outgoing_connections:
        outgoing_connections[data["channel_id"]] = set() 
    
    
    conn.sendall(b"OK")
        
def handle_incoming_voice(conn, addr, data): # incoming FROM THE CLIENT PERSPECTIVE
    outgoing_connections[data["channel_id"]].add((conn, addr[0]))
    data_queues[(conn, addr[0])] = []
    conn.sendall(b"OK")

handlers = {
    "incoming-voice": handle_incoming_voice,
    "outgoing-voice": handle_outgoing_voice
}

def handle_connection(conn, addr):
    print("New connection:", addr)
    connections[conn] = addr
    while True:
        try:
            data = conn.recv(2048)
        except:
            pass
        else:
            if not data:
                print("Disconnect:", addr)
                if conn in connections:
                    del connections[conn]
                channel = incoming_connections.get(addr)
                if channel:
                    del incoming_connections[addr]
                    outgoing_connections[channel] = set(filter(lambda x: x[1] != addr[0], outgoing_connections[channel]))
                conn.close()
                return
            try:
                parsed = json.loads(data.decode("utf-8"))
            except:
                handle_voice(conn, addr, data)
            else:
                for label in handlers:
                    if "type" in parsed and parsed["type"] == label:
                        handlers[label](conn, addr, parsed)
                        break

threading.Thread(target=rebroadcast_voice).start()

while True:
    s.listen()
    conn, addr = s.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()