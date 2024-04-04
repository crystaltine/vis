import psycopg2
import datetime
import random
from uuid import uuid4

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    return cur

cur = connect_to_db()

#test method to create server - just so I can test building a chat out of that server
def test_server_creation(data):
    server_id = str(uuid4())
    print("Server ID: " + server_id)
    server_timestamp = str(datetime.datetime.now())
    server_name = None
    server_icon = None
    server_color = None
    if data is None:
        server_id = server_id
        server_name = "test_server"
        server_icon = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
        server_color = "#ffffff"
    else:
        server_name = data["server_name"]
        server_icon = data["server_symbol"]
        server_color = data["server_color"]

    send_query='''
        INSERT into "Discord"."ServerInfo" (server_id, server__name, color, server_icon, server_creation_timestamp) values (%s, %s, %s, %s, %s)
    '''
    cur.execute(send_query, (server_id, server_name, server_color, server_icon, server_timestamp))

#creates chat given the chat data - if data is null will create a test chat with preset information
def handle_chat_creation(data):
    chat_id = str(uuid4())
    if data is None:
        server_id = input("Enter server id: ")
        chat_name = "test_chat"
        chat_type = "public" 
        chat_topic = "chat description"
        chat_order = 0  
        read_perm_level = 1  
        write_perm_level = 1
        is_dm = False
    else:
        server_id = data["server_id"]
        chat_name = data["chat_name"]
        chat_type = data["chat_type"]
        chat_topic = data["chat_topic"]
        chat_order = data["chat_order"]
        read_perm_level = data["read_perm_level"]
        write_perm_level = data["write_perm_level"]
        is_dm = data["is_dm"]

    print("Chat ID: " + chat_id)
    send_query='''
        INSERT INTO "Discord"."ChatInfo" 
        (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cur.execute(send_query, (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm))

def handle_chat_name_update(chat_id: str, new_chat_name: str) -> None:
    """
    Update the name of a chat in the database given the chat's id.

    Parameters:
        chat_id (str): The id of the chat whose name is to be updated.
        new_chat_name (str): The new name for the chat.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_name = %s
        WHERE chat_id = %s
    '''    
    cur.execute(send_query, (new_chat_name, chat_id))

def handle_chat_topic_update(chat_id: str, new_chat_topic: str) -> None:
    """
    Update the topic of a chat in the database given the chat's id.

    Parameters:
        chat_id (str): The id of the chat whose topic is to be updated.
        new_chat_topic (str): The new topic for the chat.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_topic = %s
        WHERE chat_id = %s
    '''    
    cur.execute(send_query, (new_chat_topic, chat_id))

def handle_chat_order_update(chat_id: str, new_chat_order: int) -> None:
    """
    Update the order of a chat in the database given the chat's id.

    Parameters:
        chat_id (str): The id of the chat whose order is to be updated.
        new_chat_order (int): The new order placement for the chat.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."ChatInfo"
        SET chat_order = %s
        WHERE chat_id = %s
    '''    
    cur.execute(send_query, (new_chat_order, chat_id))

def test_retrieve_chat_information(chat_id: str) -> None:
    """
    Retrieve information about a chat from the database given the chat's id.

    Parameters:
        chat_id (str): The id of the chat to retrieve information for.

    Returns:
        None
    """
    send_query = '''
        SELECT * FROM "Discord"."ChatInfo"
        WHERE chat_id = %s
    '''
    cur.execute(send_query, (chat_id,))
    records = cur.fetchall()
    if records:
        print("Chat Information:")
        for result in records:
            print("Chat ID:", result[0])
            print("Server ID:", result[1])
            print("Chat Name:", result[2])
            print("Chat Type:", result[3])
            print("Chat Topic:", result[4])
            print("Chat Order:", result[5])
            print("Read Permission Level:", result[6])
            print("Write Permission Level:", result[7])
            print("Is DM:", result[8])
            print("--------------------------------")
    else:
        print("Chat not found")

test_server_creation(None)
handle_chat_creation(None)
chat_id = input("Enter chat id: ")
test_retrieve_chat_information(chat_id)
print()
print("Updating chat name...")
print()
handle_chat_name_update(chat_id, "NEWNAME")
print()
print("Updating chat topic...")
print()
handle_chat_topic_update(chat_id, "NEW TOPIC")
print()
print("Updating chat order...")
print()
handle_chat_order_update(chat_id, 3)
test_retrieve_chat_information(chat_id)
