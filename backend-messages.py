import psycopg2
import datetime
import random
from uuid import uuid4
from typing import List
from viscord._types import MessageInfo

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"
current_position = 0
def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    return cur

cur = connect_to_db()

def handle_create_message(message_data: dict):
    message_id = str(uuid4())
    user_id = message_data["user_id"]
    server_id = message_data["server_id"]
    chat_id = message_data["chat_id"]
    replied_to_id = message_data.get("replied_to_id")
    message_content = message_data["message_content"]
    message_timestamp = str(datetime.datetime.now())
    pinged_user_ids = message_data.get("pinged_user_ids", [])

    send_query = '''
    INSERT INTO "Discord"."MessageInfo" (message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cur.execute(send_query, (message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids))

def get_recent_messages(data) -> List[MessageInfo]:
    server_id = data["server"]
    chat_id = data["chat"]

    send_query = """
    SELECT message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids
    FROM "Discord"."MessageInfo"
    WHERE server_id = %s AND chat_id = %s
    ORDER BY message_timestamp DESC
    LIMIT 15
    """
    cur.execute(send_query, (server_id,chat_id))
    messages = cur.fetchall()
    messages_data = [
        {
            "message_id": msg[0], 
            "user_id": msg[1], 
            "chat_id": msg[2], 
            "server_id": msg[3],
            "replied_to_id": msg[4], 
            "message_content": msg[5], 
            "message_timestamp": msg[6],
            "pinged_user_ids": msg[7]
        } for msg in messages
    ]
    
    return messages_data

def handle_scroll_messages(scroll_data) -> dict:
    server_id = scroll_data["server"]
    chat_id = scroll_data["chat"]
    start_pos = scroll_data["start_pos"]
    num_requested = scroll_data["num_requested"]

    send_query = """
    SELECT message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids
    FROM "Discord"."MessageInfo"
    WHERE server_id = %s AND chat_id = %s
    ORDER BY message_timestamp DESC
    OFFSET %s
    LIMIT %s
    """
    cur.execute(send_query, (server_id, chat_id, start_pos, num_requested))
    messages = cur.fetchall()
    messages_data = [{"message_id": msg[0], "user_id": msg[1], "chat_id": msg[2], "server_id": msg[3],
                      "replied_to_id": msg[4], "message_content": msg[5], "message_timestamp": msg[6].isoformat(),
                      "pinged_user_ids": msg[7]} for msg in messages]
    return messages_data

def pin_message_in_chat(chat_id, message_id):
    try:
        # Update the ChatInfo table with the new pinned message ID
        update_query = '''
        UPDATE "Discord"."ChatInfo" 
        SET pinned_message_ids = array_append(pinned_message_ids, %s) 
        WHERE chat_id = %s
        '''
        cur.execute(update_query, (message_id, chat_id))
        print("Message pinned ")
    except Exception as e:
        print("pain", e)


message_data =    {
        "user_id": "52f410df-3340-4b32-8b95-46ab5475c2be",
        "chat_id": "7885de7e-eb83-4134-ae29-0df1320177bc",
        "server_id": "acb76574-7a5c-4b5d-ab28-a8ce25982aed",
        "message_content": "Funky Banana Eating Monkeys",
        "pinged_user_ids": ["user1_id", "user2_id"]
    }

handle_create_message(message_data)
print(get_recent_messages({"server":"acb76574-7a5c-4b5d-ab28-a8ce25982aed","chat":"7885de7e-eb83-4134-ae29-0df1320177bc"}))
print("------------------------------------------------------------------------")
