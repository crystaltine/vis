import psycopg2

SERVERS = ["monkes", "fruits", "pizzas"]
CHATS = {"monkes":["ape", "gorilla", "chimp"], "fruits":["apple", "orange", "pear"], "pizzas":["chz", "pep", "hawaiian"]}

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

def reorder_chats(server_id, chat_name):
    server_id = server_id
    send_query = """select * from "Discord.ChatInfo" where server_id = %s""" #grabs all chat data for the server_id
    cur.execute(send_query, (server_id,))
    records = cur.fetchall()
    if records > 0:
        for x in range(len(records)):
            send_query = """update 1 from "Discord"."ChatInfo" set chat_order = %s where chat_order = %s""" #updates the chat_order
            if records[x][3] == chat_name: #if the chat it is updating is the same as the most recently used chat
                cur.execute(send_query, (0, x)) #sets chat_order for chat to 0 and breaks
                break
            cur.execute(send_query, (x + 1, x)) #else moves position of chat up by 1

order = 0
for x in SERVERS:
    send_query = """insert into "Discord"."SeverInfo" (server_id, server_name, color, server_icon, server_creation_timestamp)"""
    for y in CHATS[x]:
        send_query = """insert into "Discord"."ChatInfo" (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(send_query, (y, x, y, y, y, order, order, order, False))
        order += 1