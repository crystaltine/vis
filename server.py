import socket
import threading
import json

from uuid import uuid4
import random
import datetime

import psycopg2

 

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 5000))

print("Server up!")

connections = {}

def handle_message(data):
    send = json.dumps(data).encode()
    print("New message:", data["data"])
    for addr2 in connections:
        if addr2 != data["from"]:
            try:
                connections[addr2].sendall(send)
            except:
                print(f"Error sending to {addr2}, removing...")
                del connections[addr2]

def handle_account_creation(data):
    account_data = data["data"] # {"user": str (username), "password": str (password HASH)}
    
    uuid = str(uuid4())
    symbol = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    color = "#ffffff"
    timestamp = str(datetime.datetime.now())
    user = account_data["user"]
    password = account_data["password"]

    send_query='''insert into "Discord"."UserInfo" (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) values (%s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (uuid, user, password, color, symbol, timestamp))


handlers = {
    "msg": handle_message,
    "account_create": handle_account_creation

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
                    handlers[label](parsed)
                    break


while True:
    s.listen()
    conn, addr = s.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
