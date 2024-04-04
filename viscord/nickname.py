import psycopg2
import datetime
import random
from uuid import uuid4

SERVERS = ["monkes", "fruits", "pizzas"] #Testing Servers
NICKNAMES = {"monkes":["ape", "gorilla", "chimp"], "fruits":["apple", "orange", "pear"], "pizzas":["chz", "pep", "hawaiian"]} #testing members
USERNAMES = ["billy", "bob", "joe"]

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

def update_user_symbol(user_id, symbol):
    send_query = """update "Discord"."UserInfo" set user_symbol = %s where user_id = %s"""
    cur.execute(send_query, (symbol, user_id))

def update_member_nickname(server_id, user_id, nickname=None):
    send_query = """update "Discord"."MemberInfo" set nickname = %s where server_id = %s and user_id = %s"""
    if nickname == None:
        cur.execute(send_query, (user_id, server_id, user_id))
    else:
        cur.execute(send_query, (nickname, server_id, user_id))

def update_nickname_color(server_id, nickname, color):  
    send_query = """update "Discord" . "MemberInfo" set nick_color = %s where server_id = %s and user_id = %s """ 
    if color == None: 
        cur.execute(send_query, (server_id, nickname, color))


    #TESTING PAST HERE -------------------------------------------------------------------------------------------------------|

    send_query = """select * from "Discord"."MemberInfo" where server_id = %s""" #grabs all member data for the server_id
    cur.execute(send_query, (server_id,))
    records = cur.fetchall()
    print("--------------")
    for y in range(len(records)):
        print(records[y][2])


user_id_save = []
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

for y in USERNAMES:
    user_id = str(uuid4())
    user_id_save.append(user_id)
    send_query = """insert into "Discord"."UserInfo" (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) values (%s, %s, %s, %s, %s, %s)"""
    cur.execute(send_query, (user_id, y, y, y, y, server_timestamp))
    send_query = """insert into "Discord"."MemberInfo" (user_id, server_id, member_join_date) values (%s, %s, %s)"""
    cur.execute(send_query, (user_id, server_id, server_timestamp))
    order += 1
    print(y)

for y in range(len(NICKNAMES[SERVERS[0]])):
    update_member_nickname(server_id, user_id_save[y], NICKNAMES[SERVERS[0]][y])