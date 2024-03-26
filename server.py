import socket
import threading
import json

from uuid import uuid4
import random
import datetime

import psycopg2

import os

from cryptography.fernet import Fernet
key = os.getenv("VISCORD_KEY")
if not key:
    key = Fernet.generate_key()
    os.system("export VISCORD_KEY=" + key.decode())
else:
    key = key.encode()

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5000))

print("Server up!")
print("Running on " + str(s.getsockname()[0]) + ":" + str(s.getsockname()[1]))

connections = {}

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

def handle_account_creation(data, conn):
    account_data = data["data"] # {"user": str (username), "password": str (password HASH)}
    
    uuid = str(uuid4())
    symbol = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    color = "#ffffff"
    timestamp = str(datetime.datetime.now())
    user = account_data["user"]
    password = account_data["password"]



    send_query='''insert into "Discord"."UserInfo" (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) values (%s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (uuid, user, password, color, symbol, timestamp))

def handle_username_check(data, conn):
    user = data["data"]

    send_query = """select 1 from "Discord"."UserInfo" where user_name = %s"""
    cur.execute(send_query, (user,)) # weird tuple hack
    records = cur.fetchall()
    if len(records) > 0:
        conn.sendall("False".encode("utf-8"))
    else:
        conn.sendall("True".encode("utf-8"))

def handle_token_bypass(data, conn):
    data = data["data"]
    token = data["token"]
    sys_uuid = data["uuid"]

    f = Fernet(key + str(sys_uuid).encode())
    try:
        token = f.decrypt(token.encode("utf-8")).decode("utf-8")
    except:
        conn.sendall("False".encode("utf-8"))
        return
    else:
        conn.sendall(token.encode("utf-8"))



def handle_login(data, conn):
    account_data = data["data"]
    user = account_data["user"]
    password = account_data["password"]
    
    sys_uuid = account_data["sys_uuid"]

    send_query = """select user_id from "Discord"."UserInfo" where user_name = %s and user_password = %s"""
    cur.execute(send_query, (user, password))
    records = cur.fetchall()
    print(records)
    if len(records) > 0:
        token = str(uuid4())
        tokens[token] = user
        conn.sendall(token.encode("utf-8"))
        
        conn.recv(1024)

        f = Fernet(key + str(sys_uuid).encode())
        conn.sendall(f.encrypt(token.encode("utf-8")))

    else:
        conn.sendall("False".encode("utf-8"))

tokens = {}

handlers = {
    "msg": handle_message,
    "account_create": handle_account_creation,
    "username_check": handle_username_check,
    "login": handle_login,
    "token_bypass": handle_token_bypass

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
                    print("Endpoint " + label + " called by " + str(addr))
                    handlers[label](parsed, conn)
                    break


while True:
    s.listen()
    conn, addr = s.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
