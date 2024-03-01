import socket
import threading
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 9999))

print("Server up!")

connections = {}

def handle_message(data):
    send = json.dumps(data).encode()
    print("New message:", data["data"])
    for addr2 in connections:
        if addr2 != data["from"]:
            connections[addr2].sendall(send)

handlers = {
    "msg": handle_message
}

def handle_connection(conn, addr):
    print("New connection:", addr)
    connections[addr] = conn
    while True:
        try:
            data = conn.recv(1024)
        except:
            pass
        else:
            parsed = json.loads(data.decode())
            for label in handlers:
                if "type" in parsed and parsed["type"] == label:
                    parsed["from"] = addr
                    handlers[label](parsed)
                    break

while True:
    s.listen()
    conn, addr = s.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
