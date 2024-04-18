
import uuid
import hashlib
import socket
import json

username = "test_user_1"
password = "randomsecretpassword45"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("localhost", 5000))

s.send(json.dumps({
    "type": "login", 
    "data": {
        "user": username, 
        "password": password,
        "sys_uuid": uuid.getnode()
    }
}).encode())

response = s.recv(1024)
print(response)

s.sendall(b'ok')

response = s.recv(1024)
print(response)