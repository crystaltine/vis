from .db import cur
from .roles import get_server_perms
from uuid import uuid4

def reorder_chats(server_id: str, chat_id: str):
    # TODO - use chat_id instead of chat_name (since we can have duplicate names)
    # does this function move the specified chat to top? If so, rename the function
    send_query = """select * from "Discord"."ChatInfo" where server_id = %s"""
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

def handle_reorder_chats(data, conn):
    server_id = data["data"]["server_id"]
    chat_name = data["data"]["chat_name"]
    try:
        reorder_chats(server_id, chat_name)
        conn.sendall("True".encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))

def handle_chat_creation(user_id: str, server_id: str, chat_name: str, chat_type: str, chat_topic: str, chat_order: int, read_perm_level: int, write_perm_level: int, is_dm: bool):
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
        None
    """
    
    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        print("You do not have permission to create a chat")
        return

    chat_id = str(uuid4())

    send_query='''
        INSERT INTO "Discord"."ChatInfo" 
        (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cur.execute(send_query, (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm))

def handle_chat_name_update(user_id: str, server_id: str, chat_id: str, new_chat_name: str) -> None:
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
        None
    """

    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        print("You do not have permission to change the chat name")
        return
    
    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_name = %s
        WHERE chat_id = %s
    '''    
    cur.execute(send_query, (new_chat_name, chat_id))

def handle_chat_topic_update(user_id: str, server_id: str, chat_id: str, new_chat_topic: str) -> None:
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
        None
    """

    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        print("You do not have permission to change the chat topic")
        return

    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_topic = %s
        WHERE chat_id = %s
    '''    
    cur.execute(send_query, (new_chat_topic, chat_id))

def handle_chat_order_update(user_id: str, server_id: str, chat_id: str, new_chat_order: int) -> None:
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
        None
    """

    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        print("You do not have permission to change the chat prder")
        return

    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_order = %s
        WHERE chat_id = %s
    '''    
    cur.execute(send_query, (new_chat_order, chat_id))

def handle_chat_deletion(user_id: str, server_id: str, chat_id: str):
    """
    Deletes the chat in the database given the chat's id. It first checks whether
    the user making the request has the necessary permissions to manage the chat. If the user does not have
    permission, it prints a message indicating so and returns without updating the database.

    Parameters:
        user_id (str): The id of the user making the request.
        server_id (str): The id of the server the chat is in.
        chat_id (str): The id of the chat whose order is to be updated.

    Returns:
        None
    """

    perms = get_server_perms(user_id, server_id)

    if not perms["manage_chats"]:
        print("You do not have permission to delete the chat")
        return
    
    send_query = '''
        DELETE FROM "Discord"."ChatInfo"
        WHERE chat_id = %s AND server_id = %s
    '''    

    cur.execute(send_query, (chat_id, server_id))