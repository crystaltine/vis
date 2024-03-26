import socket
import threading
import json

from uuid import uuid4
import random
import datetime
 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 5000))

print("Up on ", s.getsockname())

def handle_connection(conn, addr):
    print("Connected to", addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(data)

s.listen()
while True:
    try:
        conn, addr = s.accept()
    except KeyboardInterrupt:
        s.close()
        break
    threading.Thread(target=handle_connection, args=(conn, addr)).start()