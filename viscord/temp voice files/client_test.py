import socket
import threading
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 5000))
import time
while True:
    s.send(sys.argv[1].encode())
    time.sleep(0.1)