import socket
import os, sys
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

import json
s.connect(("127.0.0.1", 9999))

def handle_message(data):
    print(f"{data['id']}: {data['data']}")

handlers = {
   "msg": handle_message 
}

def get_data():
    while True:
        try:
            data = s.recv(1024)
        except Exception as e:
            raise
        else:
            parsed = json.loads(data.decode())
            for label in handlers:
                if "type" in parsed and parsed["type"] == label:
                    handlers[label](parsed)
                    break

threading.Thread(target=get_data).start()

username = input("Username: ")
while True:
    m = input("")
    if m == "quit":
        os._exit(0)
    data = {
        "type": "msg",
        "data": m,
        "id": username
    }

    s.sendall(json.dumps(data).encode())
