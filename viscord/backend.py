import psycopg2
import blessed
import datetime
from typing import Literal

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    return cur

db = connect_to_db()

def DB_reply_to_message(user_id, message_id, chat_id, replied_to_id, server_id, message_content) -> Literal["success", "failure", "unavailable"]:
    try: 
        send_query = '''SELECT replied_to_id FROM "Discord"."MessageInfo" WHERE (replied_to_id = %s)'''
        db.execute(send_query, (replied_to_id))
        data = db.fetchall()
        if len(data) == 0:
            return "failure"
        else: 
            send_query='''UPDATE "Discord". "MessageInfo" (user_id, message_id, chat_id, server_id, message_content, message_timestamp) values (%s, %s, %s, %s, %s, %s) WHERE replied_to_id = %s'''
            message_timestamp = str(datetime.datetime.now)
            db.execute(send_query, (user_id, message_id, chat_id, server_id, message_content, message_timestamp, replied_to_id))
            return "success"
    except: 
        return "unavailable"

    

    


