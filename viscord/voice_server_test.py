import socket
import threading
import json

from uuid import uuid4
import random
import datetime


 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 5000))

print("Server up!")
print("Running on " + str(s.getsockname()[0]) + ":" + str(s.getsockname()[1]))


connections = {}

def handle_voice(conn, data):
    for addr2 in connections:
        try:
            connections[addr2].sendall(data)
        except:
            pass

def handle_connection(conn, addr):
    print("New connection:", addr)
    connections[addr] = conn
    while True:
        try:
            data = conn.recv(1024)
        except:
            pass
        else:
            if not data:
                print("Disconnect:", addr)
                del connections[addr]
                return
            handle_voice(conn, data)

while True:
    s.listen()
    conn, addr = s.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
