import socket
import threading
import json
import os
from typing import Dict, Tuple
import api.users, api.login_flow, api.messages, api.chats
import ipaddress
from multiprocessing import Process

basepath = os.path.dirname(os.path.realpath(__file__))
blacklist = []

with open(os.path.join(basepath, "blacklist.txt")) as f:
    for line in f.read().split("\n"):
        if "/" in line:
            blacklist.append(ipaddress.ip_network(line))
        else:
            blacklist.append(ipaddress.ip_address(line))


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5001))

print("Server up!")
print("Running on " + str(s.getsockname()[0]) + ":" + str(s.getsockname()[1]))

connections: Dict[Tuple[str, int], socket.socket] = {}



def handle_message(data, conn):
    send = json.dumps(data).encode()
    print("New message:", data["data"])
    for addr2 in connections:
        if addr2 != data["from"]:
            try:
                connections[addr2].sendall(send)
            except:
                print(f"Error sending to {addr2}, removing...")
                del connections[addr2]

tokens = {}
handlers = {
    "msg": handle_message,
#    "account_create": api.users.handle_account_creation,
#    "username_check": api.users.handle_username_check,
#    "login": api.login_flow.handle_login,
#    "token_bypass": api.login_flow.handle_token_bypass,
#    "pin_message": api.messages.pin_message_endpoint,
#    "handle_user_name_update": api.users.update_username_endpoint,
#    "handle_user_password_update": api.users.update_password_endpoint,
#    "handle_user_color_update": api.users.update_color_endpoint,
#    "handle_user_symbol_update": api.users.update_symbol_endpoint,
#    "handle_reorder_chats": api.chats.handle_reorder_chats,
#  
#
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
            if not data:
                print("Disconnect:", addr)
                del connections[addr]
                return
            parsed = json.loads(data.decode())
            for label in handlers:
                if "type" in parsed and parsed["type"] == label:
                    parsed["from"] = addr
                    print("Endpoint " + label + " called by " )
                    handlers[label](parsed, conn)
                    break

def socket_accept_thread():
    s.listen()

    while True: 
        try:
            print(f"bef accept")
            conn, addr = s.accept()
            print(f"aft accept")
        except OSError as err:
            # connection probably closed
            break

        # check blacklist
        for net in blacklist:
            if (isinstance(net, ipaddress.ip_address) and ipaddress.ip_address(addr[0]) == net) or (isinstance(net, ipaddress.ip_network) and ipaddress.ip_address(addr[0]) in net):
                print("Blocked connection from " + addr[0])
                conn.close()
                continue

        threading.Thread(target=handle_connection, args=(conn, addr)).start()
    
socket_thread = threading.Thread(target=socket_accept_thread)
socket_thread.start()

from api.flask_app import app
from api import login_flow, chats, friends, invites, members, messages, roles, servers, users
from api import db

from flask import request
import requests

from api import server_config as sc
from uuid import uuid4

@app.route("/")
def index():
    ...

    ip = request.remote_addr
    json_data = requests.get("http://ipapi.co/" + ip + "/json").json()
    if "latitude" not in json_data or "longitude" not in json_data:
        return "Error checking geolocation"
    
    SEA_LAT = 47.6061
    SEA_LONG = 122.3328

    if abs(json_data["latitude"] - SEA_LAT) > 1 or abs(json_data["longitude"] - SEA_LONG) > 1:
        return f"<h1>Viscord</h1><br><p>This address is intended for the Viscord project.<br>Your IP address is <b>{request.remote_addr}</b><br>This service is only intended for users in or around Seattle, WA.</p>"
    else:
        return "<h1>Viscord</h1><br><p>Welcome to Viscord."

def apprun():
    app.run(host=sc.HOST, port=sc.HTTP_PORT)

if __name__ == "__main__":
    http_process = Process(target=apprun)
    http_process.start()

    # cli
    while True:
        cmd = input("> ")
        if cmd in ["exit", "quit", "stop"]:
            s.close()
            print(f"1")
            socket_thread.join()
            print(f"2")
            http_process.terminate()
            http_process.join()
            exit(0)
        elif cmd == "help":
            print("\x1b[33mno!!")
        else:
            print("\x1b[0mUnknown command. Type 'help' for a list of commands.")