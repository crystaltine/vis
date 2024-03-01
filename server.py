import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(("127.0.0.1", 9999))

print("Server up!")

connections = {}

def handle_connection(conn, addr):
    connections[addr] = conn
    while True:
        try:
            data = conn.recv(1024)
        except: pass
        else:
            decoded = data.decode()
            if decoded == "quit":
                conn.close()
                del connections[addr]
                return
            else:
                for addr2 in connections:
                    if addr2 != addr:
                        addr.sendall(data)

while True:
    s.listen()
    conn, addr = s.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
