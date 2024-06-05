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



connected_clients = {
    # user id: {
    #    target id: connection
    # }
}

channels = {}

lifelines = {}


@app.route("/api/voice/join", methods=["POST"])
def join_voice() -> Literal["success", "failure"]:
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
    
    ...
    # TODO: figure out???


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
                lifelines[uid].send(json.dumps(data).encode())

    return Response(json.dumps(return_data), status=200)

def handle_client(conn, addr):
    data = conn.recv(1024)
    data = json.loads(data.decode())
    
    user_id = data["id"]
    role = data["role"]
    if role == "receiver":
        target = data["target"]
        if target not in connected_clients: 
            connected_clients[target] = {}
        connected_clients[target][user_id] = conn
        print(f"NEW RECEIVER: {target} -> {id}")
    elif role == "lifeline":
        lifelines[user_id] = conn
        print(f"NEW LIFELINE: {id}")
    elif role == "sender":
        if user_id not in connected_clients:
            connected_clients[user_id] = {}
        print(f"SENDER ESTABLISHED: {id}")
    
    while True:
        try:
            data = conn.recv(2048)
        except:
            ...
            # TODO: handle disconnect - prioritize lifelines first
            return
        if role == "sender":
            if user_id not in connected_clients: continue
            for target in connected_clients[user_id]:
                try:
                    connected_clients[user_id][target].send(data)
                except:
                    pass
    


def spawn_socket():
    s.listen()
    while True:
        client, addr = s.accept()
        threading.Thread(target=handle_client, args=(client, addr)).start()

threading.Thread(target=spawn_socket).start()