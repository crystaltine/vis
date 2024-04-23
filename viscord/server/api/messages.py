from .db import cur
from uuid import uuid4
import datetime
from typing import Literal, List
from ._types import *
from logger import Logger

def pin_message(chat_id: str, message_id: str) -> Literal['success', 'failure']:
    try:
        # Update the ChatInfo table with the new pinned message ID
        update_query = '''
        UPDATE "Discord"."ChatInfo" 
        SET pinned_message_ids = array_append(pinned_message_ids, %s) 
        WHERE chat_id = %s
        '''
        cur.execute(update_query, (message_id, chat_id))
        return 'success'
    except Exception as e:
        Logger.err(f"couldn't pin message: {e}", 'pin_message')
        return 'failure'

def handle_pin_message(data, conn):
    data = data["data"]
    message_id = data["message_id"]
    channel_id = data["channel_id"]

    if pin_message(message_id, channel_id):
        if conn:
            conn.sendall("True".encode("utf-8"))
    else:
        if conn:
            conn.sendall("False".encode("utf-8"))

def create_message(message_data: dict) -> Literal['success', 'failure', 'incomplete-data']:
    """
    Creates a database entry for a message. Provide the following fields in `message_data`:
    - user_id
    - server_id
    - chat_id
    - replied_to_id (optional)
    - message_content
    - pinged_user_ids (empty list if no pings)

    returns 'incomplete-data' if the above requirements were not met.
    """
    # assert necessary fields exist
    for required_field in ['user_id', 'server_id', 'chat_id', 'message_content', 'pinged_user_ids']:
        if required_field not in message_data.keys():
            print(f"\x1b[31m[create_message]: message data field not provided: {required_field}\x1b[0m")
            return 'incomplete_data'

    message_id = str(uuid4())
    user_id = message_data["user_id"]
    server_id = message_data["server_id"]
    chat_id = message_data["chat_id"]
    replied_to_id = message_data.get("replied_to_id")
    message_content = message_data["message_content"]
    message_timestamp = datetime.datetime.now()
    pinged_user_ids = message_data["pinged_user_ids"]

    send_query = '''
    INSERT INTO "Discord"."MessageInfo" (message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''
    try:
        cur.execute(send_query, (message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids))
        return 'success'
    except Exception as e:
        Logger.err(f"couldn't put message in db: {e}", 'create_message')
        return 'failure'
    
def handle_message_creation(data, conn):
    message_data = data["data"]
    conn.sendall(create_message(message_data).encode("utf-8"))

def get_recent_messages(chat_id: str, num: int = 15) -> List[MessageInfo]:
    """
    Returns the most recently sent messages in a chat.
    `num` specifies how many to return (default 15)
    """

    send_query = """
    SELECT message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids
    FROM "Discord"."MessageInfo"
    WHERE chat_id = %s
    ORDER BY message_timestamp DESC
    LIMIT %s
    """
    cur.execute(send_query, (chat_id, num))
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

def handle_get_recent_messages(data, conn):
    chat_id = data["data"]["chat_id"]
    num = data["data"].get("num", 15)
    messages = get_recent_messages(chat_id, num)
    conn.sendall(str(messages).encode("utf-8"))

def get_message_chunk(chat_id: str, offset: int, num: int) -> List[MessageInfo]:
    send_query = """
    SELECT *
    FROM "Discord"."MessageInfo"
    WHERE chat_id = %s
    ORDER BY message_timestamp DESC
    OFFSET %s
    LIMIT %s
    """
    cur.execute(send_query, (chat_id, offset, num))
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

def message_chunk_endpoint(data, conn):
    chat_id = data["data"]["chat_id"]
    offset = data["data"]["offset"]
    num = data["data"]["num"]
    messages = get_message_chunk(chat_id, offset, num)
    conn.sendall(str(messages).encode("utf-8"))