import socket
import threading
import json

from uuid import uuid4
import random
import datetime


 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5000))

print("Server up!")
print("Running on " + str(s.getsockname()[0]) + ":" + str(s.getsockname()[1]))


connections = {}

incoming_connections = {}
outgoing_connections = {}

no_voice_echo = False

def handle_voice(conn, addr, data):
    channel_id = incoming_connections.get(addr)
    if channel_id:
        for conn2, addr2 in outgoing_connections[channel_id]:
            if not no_voice_echo or (addr2 != addr[0]):
                conn2.sendall(data)

def handle_outgoing_voice(conn, addr, data):
    if conn not in incoming_connections:
        incoming_connections[addr] = data["channel_id"]
    if data["channel_id"] not in outgoing_connections:
        outgoing_connections[data["channel_id"]] = set()
    conn.sendall(b"OK")
        
def handle_incoming_voice(conn, addr, data):
    outgoing_connections[data["channel_id"]].add((conn, addr[0]))
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


while True:
    s.listen()
    conn, addr = s.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
