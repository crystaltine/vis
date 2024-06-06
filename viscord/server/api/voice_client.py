from .db import cur
from .roles import chat_perms_wrapper
from uuid import uuid4
from flask import request, Response
from .flask_app import app
from .helpers import *
import requests
from .server_config import URI, VOICE_PORT, HOST
from typing import *

import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, VOICE_PORT))

class GlobalState:
    def __init__(self):
        self._lock = threading.Lock()
        self._channels = {}
        self._lifelines = {}
        self._connected_clients = {}

    @property
    def channels(self):
        with self._lock:
            return self._channels.copy()

    @property
    def lifelines(self):
        with self._lock:
            return self._lifelines.copy()

    @property
    def connected_clients(self):
        with self._lock:
            return self._connected_clients.copy()

    def add_to_channels(self, chat_id, user_id):
        with self._lock:
            if chat_id not in self._channels:
                self._channels[chat_id] = set()
            self._channels[chat_id].add(user_id)

    def add_to_lifelines(self, user_id, conn):
        with self._lock:
            self._lifelines[user_id] = conn

    def add_to_clients(self, user_id, target, conn, direction=1, blank_dict=False): # 1 for uid -> target, 2 for target -> uid
        a = user_id
        b = target
        if direction == 2:
            a, b = b, a
        with self._lock:
            if a not in self._connected_clients:
                self._connected_clients[a] = {}
            if not blank_dict: self._connected_clients[a][b] = conn

global_state = GlobalState()



@app.route("/api/voice/join", methods=["POST"])
def join_voice() -> Literal["success", "failure"]:

    channels = global_state.channels
    lifelines = global_state.lifelines
    connected_clients = global_state.connected_clients

    """
    Join a voice channel.
    """
    
    if not validate_fields(request.json, {"user_token": str, "server_id": str, "chat_id": str}):
        return invalid_fields()
    
    user_id = get_user_id(request.json["user_token"])
    server_id = request.json["server_id"]
    chat_id = request.json["chat_id"]
    
    perms = chat_perms_wrapper(user_id, server_id, chat_id)
    if not perms["readable"]:
        return missing_permissions()

    if chat_id not in channels:
        channels[chat_id] = set()
        channels[chat_id].add(user_id)
        return_data = {"type": "callback", "connections": ["lifeline"]}
    else:
        # connections = list(connected_clients[chat_id].keys())
        connections = list(channels[chat_id])
        if len(connections) == 0:
            return_data = {"type": "callback", "connections": ["lifeline"]}
        else:
            return_data = {"type": "callback", "connections": connections + ["lifeline"]}


        data = {"msg": "join", "chat_id": chat_id, "id": user_id}
        for uid in channels[chat_id]:
            if uid != user_id:
                global_state.lifelines[uid].send(json.dumps(data).encode())

    return Response(json.dumps(return_data), status=200)

def handle_client(conn, addr):
    channels = global_state.channels
    lifelines = global_state.lifelines
    connected_clients = global_state.connected_clients
    
    
    data = conn.recv(1024)
    data = json.loads(data.decode())
    
    user_id = data["id"]
    role = data["role"]
    if role == "receiver":
        target = data["target"]
        global_state.add_to_clients(user_id, target, conn, direction=2)
        print(f"NEW RECEIVER: {target} -> {user_id}")
    elif role == "lifeline":
        global_state.add_to_lifelines(user_id, conn)
        print(f"NEW LIFELINE: {user_id} ({hash(user_id)})")
        print(global_state.lifelines)
    elif role == "sender":
        # TODO
        global_state.add_to_clients(user_id, None, None, blank_dict=True)
        print(f"SENDER ESTABLISHED: {user_id}")
    
    while True:
        try:
            data = conn.recv(2048)
        except Exception as e:
            ...
            # TODO: handle disconnect - prioritize lifelines first
            print(e)
            return
        if role == "sender":
            if user_id not in global_state.connected_clients:
                print("a")
                continue
            for target in global_state.connected_clients[user_id]:
                try:
                    global_state.connected_clients[user_id][target].send(data)
                except Exception as e:
                    print(e)
                    pass
    


def spawn_socket():
    s.listen()
    while True:
        client, addr = s.accept()
        threading.Thread(target=handle_client, args=(client, addr)).start()

threading.Thread(target=spawn_socket).start()
