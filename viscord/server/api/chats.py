from .db import cur
from .roles import get_server_perms
from uuid import uuid4
from flask import request, Response
from flask_app import app
from .helpers import *

@app.route("/api/chats/create", methods=["POST"])
def reorder_chats():

    if not validate_fields(request.json, {"server_id": str, "chat_id": str}):
        return invalid_fields()
    
    server_id = request.json["server_id"]
    chat_id = request.json["chat_id"]

    # TODO - use chat_id instead of chat_name (since we can have duplicate names)
    # does this function move the specified chat to top? If so, rename the function
    try:
        send_query = """select * from "Discord"."ChatInfo" where server_id = %s"""
        cur.execute(send_query, (server_id,))
        records = cur.fetchall()
        cur_chat = records[0][3]
        if len(records) > 0:
            for x in range(len(records)):
                change_chat = cur_chat
                send_query = """update "Discord"."ChatInfo" set chat_order = %s where chat_id = %s""" #updates the chat_order
                if records[x][3] == chat_id: #if the chat it is updating is the same as the most recently used chat
                    cur.execute(send_query, (0, change_chat)) #sets chat_order for chat to 0 and breaks
                    break
                cur_chat = records[x + 1][3]
                cur.execute(send_query, ((x + 1), change_chat)) #else moves position of chat up by 1
        return return_success()
    except Exception as e:
        return return_error(e)

@app.route("/api/chats/create", methods=["POST"])
def handle_chat_creation():
    """
    Creates a new chat using the given data and inserts it into the database. Checks if the user creating the chat
    has the necessary permissions to create a chat. If the user does not have permission, it prints a message indicating so.

    Parameters:
        user_id (str): The ID of the user creating the chat.
        server_id (str): The ID of the server to which the chat belongs.
        chat_name (str): The name of the chat.
        chat_type (str): The type of the chat (e.g., "text chat", "voice chat", etc.).
        chat_topic (str): The topic or description of the chat.
        chat_order (int): The order the chat appears in the server.
        read_perm_level (int): The permission level required to read messages in the chat.
        write_perm_level (int): The permission level required to write messages in the chat.
        is_dm (bool): A boolean indicating whether the chat is a direct message (DM) chat.

    Returns:
        bool
    """
    if not validate_fields(request.json, {"user_id": str, "server_id": str, "chat_name": str, "chat_type": str, "chat_topic": str, "chat_order": int, "read_perm_level": int, "write_perm_level": int, "is_dm": bool}):
        return invalid_fields()
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    chat_name = request.json["chat_name"]
    chat_type = request.json["chat_type"]
    chat_topic = request.json["chat_topic"]
    chat_order = request.json["chat_order"]
    read_perm_level = request.json["read_perm_level"]
    write_perm_level = request.json["write_perm_level"]
    is_dm = request.json["is_dm"]

    
    try:
        perms = get_server_perms(user_id, server_id) # NOTE this doesn't work for dms, those will be for sprint 3

        if not perms["manage_chats"]:
            return False

        chat_id = str(uuid4())

        send_query='''
            INSERT INTO "Discord"."ChatInfo" 
            (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cur.execute(send_query, (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm))
        return return_success()
    except Exception as e:
        return return_error(e)
        

@app.route("/api/chats/update/name", methods=["POST"])
def handle_chat_name_update() -> bool:
    """
    Update the name of a chat in the database given the chat's id. It first checks whether
    the user making the request has the necessary permissions to manage the chat. If the user does not have
    permission, it prints a message indicating so and returns without updating the database.

    Parameters:
        user_id (str): The id of the user making the request.
        server_id (str): The id of the server the chat is in.
        chat_id (str): The id of the chat whose name is to be updated.
        new_chat_name (str): The new name for the chat.

    Returns:
        bool
    """
    if not validate_fields(request.json, {"user_id": str, "server_id": str, "chat_id": str, "new_chat_name": str}):
        return invalid_fields()
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    chat_id = request.json["chat_id"]
    new_chat_name = request.json["new_chat_name"]


    
    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        return missing_permissions()
    
    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_name = %s
        WHERE chat_id = %s
    '''    
    try:
        cur.execute(send_query, (new_chat_name, chat_id))
        return return_success()
    except Exception as e:
        return return_error(e)

@app.route("/api/chats/update/topic", methods=["POST"])
def handle_chat_topic_update() -> bool:
    """
    Update the topic of a chat in the database given the chat's id. It first checks whether
    the user making the request has the necessary permissions to manage the chat. If the user does not have
    permission, it prints a message indicating so and returns without updating the database.

    Parameters:
        user_id (str): The id of the user making the request.
        server_id (str): The id of the server the chat is in.
        chat_id (str): The id of the chat whose topic is to be updated.
        new_chat_topic (str): The new topic for the chat.

    Returns:
        bool
    """
    if not validate_fields(request.json, {"user_id": str, "server_id": str, "chat_id": str, "new_chat_topic": str}):
        return invalid_fields()
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    chat_id = request.json["chat_id"]
    new_chat_topic = request.json["new_chat_topic"]

    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        return missing_permissions()
    
    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_topic = %s
        WHERE chat_id = %s
    '''    
    try:
        cur.execute(send_query, (new_chat_topic, chat_id))
        return return_success()
    except Exception as e:
        return return_error(e)

@app.route("/api/chats/update/order", methods=["POST"])
def handle_chat_order_update(user_id: str, server_id: str, chat_id: str, new_chat_order: int) -> bool:
    """
    Update the order of a chat in the database given the chat's id. It first checks whether
    the user making the request has the necessary permissions to manage the chat. If the user does not have
    permission, it prints a message indicating so and returns without updating the database.

    Parameters:
        user_id (str): The id of the user making the request.
        server_id (str): The id of the server the chat is in.
        chat_id (str): The id of the chat whose order is to be updated.
        new_chat_order (int): The new order placement for the chat.

    Returns:
        bool
    """
    if not validate_fields(request.json, {"user_id": str, "server_id": str, "chat_id": str, "new_chat_order": int}):
        return invalid_fields()
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    chat_id = request.json["chat_id"]
    new_chat_order = request.json["new_chat_order"]


    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        return missing_permissions()

    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_order = %s
        WHERE chat_id = %s
    '''    
    try:
        cur.execute(send_query, (new_chat_order, chat_id))
        return return_success()
    except Exception as e:
        return return_error(e)
    
@app.route("/api/chats/delete", methods=["POST"])
def handle_chat_deletion():
    """
    Deletes the chat in the database given the chat's id. It first checks whether
    the user making the request has the necessary permissions to manage the chat. If the user does not have
    permission, it prints a message indicating so and returns without updating the database.

    Parameters:
        user_id (str): The id of the user making the request.
        server_id (str): The id of the server the chat is in.
        chat_id (str): The id of the chat whose order is to be updated.

    Returns:
        bool
    """
    if not validate_fields(request.json, {"user_id": str, "server_id": str, "chat_id": str}):
        return invalid_fields()
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    chat_id = request.json["chat_id"]

    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        return missing_permissions()
    
    send_query = '''
        DELETE FROM "Discord"."ChatInfo"
        WHERE chat_id = %s AND server_id = %s
    '''    

    
    try:
        cur.execute(send_query, (chat_id, server_id))
        return return_success()
    except Exception as e:
        return return_error(e)