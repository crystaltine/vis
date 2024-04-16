from .db import cur
from cryptography.fernet import Fernet
import os
from uuid import uuid4

from cryptography.fernet import Fernet
key = os.getenv("VISCORD_KEY")
if not key:
    key = Fernet.generate_key()
    os.system("export VISCORD_KEY=" + key.decode())
else:
    key = key.encode()

tokens = {}

def handle_login(data, conn):
    account_data = data["data"]
    user = account_data["user"]
    password = account_data["password"]
    
    sys_uuid = account_data["sys_uuid"]

    send_query = """select 1 from "Discord"."UserInfo" where user_name = %s and user_password = %s"""
    cur.execute(send_query, (user, password))
    records = cur.fetchall()
    if len(records) > 0:
        token = str(uuid4())
        tokens[token] = user
        conn.sendall(token.encode("utf-8"))
    else:   
        
        conn.recv(1024)

        f = Fernet(key + str(sys_uuid).encode())
        conn.sendall(f.encrypt(token.encode("utf-8")))


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