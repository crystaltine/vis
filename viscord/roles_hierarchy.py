from typing import List
from typing import Dict
import psycopg2
from _types import *

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

from typing import List
from typing import Dict
import psycopg2
from _types import *
from uuid import uuid4

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

# Given a user_id, a server_id, and a chat_id, this function will return a dict containing a bool for reading and a bool for writing perms


# print(get_chat_perms())
# print(get_server_perms())
# server_id='ad3f1cd8-ffcd-48ca-abc7-9409c17c9122'
# role_info={"role_name":'test_role', "role_color":'#ffffff', "role_symbol":"★", "priority":3, "permissions":2, "manage_server":False, "manage_chats":False, \
#            "manage_members":False, "manage_roles":True, "manage_voice":True,  "manage_messages":True, "is_admin":False}
# user_id='b98757df-71aa-4615-8345-26c71cfbb304'
# add_role(server_id, role_info, user_id)

role_id='5a440e84-96b1-4caa-865e-fdc4a54d4e12'
server_id='ad3f1cd8-ffcd-48ca-abc7-9409c17c9122'
remove_role(role_id, server_id)