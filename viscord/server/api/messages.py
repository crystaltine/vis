from .db import cur
from uuid import uuid4
import datetime
from typing import Literal, List
from ._types import *
from .flask_app import app
from .helpers import *
from flask import request, Response


@app.route("/api/messages/pin", methods=["POST"])
def pin_message() -> Literal['success', 'failure']:
    
    if not validate_fields(request.json, {"message_id": str, "chat_id": str}):
        return invalid_fields()
    
    message_id = request.json["message_id"]
    chat_id = request.json["chat_id"]

    try:
        # Update the ChatInfo table with the new pinned message ID
        update_query = '''
        UPDATE "Discord"."ChatInfo" 
        SET pinned_message_ids = array_append(pinned_message_ids, %s) 
        WHERE chat_id = %s
        '''
        cur.execute(update_query, (message_id, chat_id))
        return return_success()
    except Exception as e:
        return return_error(e)

@app.route("/api/messages/send", methods=["POST"])
def create_message() -> Literal['success', 'failure', 'incomplete-data']:
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
    # for required_field in ['user_id', 'server_id', 'chat_id', 'message_content', 'pinged_user_ids']:
    #     if required_field not in message_data.keys():
    #         print(f"\x1b[31m[create_message]: message data field not provided: {required_field}\x1b[0m")
    #         return 'incomplete_data'

    if not validate_fields(request.json, {"user_id": str, "server_id": str, "chat_id": str, "message_content": str, "pinged_user_ids": list}):
        return invalid_fields()
    
    message_data = request.json

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
        return return_success()
    except Exception as e:
        return return_error(e)
    
@app.route("/api/messages/get_recent", methods=["POST"])
def get_recent_messages() -> List[MessageInfo]:
    """
    Returns the most recently sent messages in a chat.
    `num` specifies how many to return (default 15)
    """

    if not validate_fields(request.json, {"chat_id": str, "num": int}):
        return invalid_fields()
    
    chat_id = request.json["chat_id"]
    num = request.json.get("num", 15)

    send_query = """
    SELECT message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids
    FROM "Discord"."MessageInfo"
    WHERE chat_id = %s
    ORDER BY message_timestamp DESC
    LIMIT %s
    """
    try:
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
        
        return Response(json.dumps({"type": "success", "data": messages_data}), status=200)
    except Exception as e:
        return return_error(e)

@app.route("/api/messages/get_chunk", methods=["POST"])
def get_message_chunk() -> List[MessageInfo]:

    if not validate_fields(request.json, {"chat_id": str, "offset": int, "num": int}):
        return invalid_fields()
    
    chat_id = request.json["chat_id"]
    offset = request.json["offset"]
    num = request.json["num"]

    send_query = """
    SELECT *
    FROM "Discord"."MessageInfo"
    WHERE chat_id = %s
    ORDER BY message_timestamp DESC
    OFFSET %s
    LIMIT %s
    """
    try:
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
        return Response(json.dumps({"type": "success", "data": messages_data}), status=200)
    except Exception as e:
        return return_error(e)

