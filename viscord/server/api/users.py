import datetime
from db import cur
from uuid import uuid4
import random



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