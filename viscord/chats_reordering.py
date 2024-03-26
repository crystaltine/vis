import psycopg2
import datetime
import random
from uuid import uuid4

SERVERS = ["monkes", "fruits", "pizzas"] #Testing Servers
CHATS = {"monkes":["ape", "gorilla", "chimp"], "fruits":["apple", "orange", "pear"], "pizzas":["chz", "pep", "hawaiian"]} #testing chats

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

def reorder_chats(server_id, chat_name):
    server_id = server_id
    send_query = """select * from "Discord"."ChatInfo" where server_id = %s""" #grabs all chat data for the server_id
    cur.execute(send_query, (server_id,))
    records = cur.fetchall()
    cur_chat = records[0][3]
    if len(records) > 0:
        for x in range(len(records)):
            change_chat = cur_chat
            send_query = """update "Discord"."ChatInfo" set chat_order = %s where chat_name = %s""" #updates the chat_order
            if records[x][3] == chat_name: #if the chat it is updating is the same as the most recently used chat
                cur.execute(send_query, (0, change_chat)) #sets chat_order for chat to 0 and breaks
                break
            cur_chat = records[x + 1][3]
            cur.execute(send_query, ((x + 1), change_chat)) #else moves position of chat up by 1



    #TESTING PAST HERE -------------------------------------------------------------------------------------------------------|

    send_query = """select * from "Discord"."ChatInfo" where server_id = %s""" #grabs all chat data for the server_id
    cur.execute(send_query, (server_id,))
    records = cur.fetchall()
    print("--------------")
    for y in range(len(records)):
        print(records[y][2])
order = 0
server_id = str(uuid4())
print("Server ID: " + server_id)
server_timestamp = str(datetime.datetime.now())
server_name = None
server_icon = None
server_color = None
server_id = server_id
server_name = "test_server"
server_icon = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
server_color = "#ffffff"
send_query='''
    INSERT into "Discord"."ServerInfo" (server_id, server__name, color, server_icon, server_creation_timestamp) values (%s, %s, %s, %s, %s)
'''
cur.execute(send_query, (server_id, server_name, server_color, server_icon, server_timestamp))

for y in CHATS[SERVERS[0]]:
    chat_id = str(uuid4())
    send_query = """insert into "Discord"."ChatInfo" (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cur.execute(send_query, (chat_id, server_id, y, y, y, order, order, order, False))
    order += 1
    print(y)

reorder_chats(server_id, "chimp")

