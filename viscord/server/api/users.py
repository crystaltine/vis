import datetime
from db import cur
from uuid import uuid4
import random



def handle_account_creation(data, conn):
    account_data = data["data"] # {"user": str (username), "password": str (password HASH)}
    
    uuid = str(uuid4())
    symbol = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    color = "#ffffff"
    timestamp = str(datetime.datetime.now())
    user = account_data["user"]
    password = account_data["password"]



    send_query='''insert into "Discord"."UserInfo" (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) values (%s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (uuid, user, password, color, symbol, timestamp))

def handle_username_check(data, conn):
    user = data["data"]

    send_query = """select 1 from "Discord"."UserInfo" where user_name = %s"""
    cur.execute(send_query, (user,)) # weird tuple hack
    records = cur.fetchall()
    if len(records) > 0:
        conn.sendall("False".encode("utf-8"))
    else:
        conn.sendall("True".encode("utf-8"))

def handle_user_name_update(user_id: str, new_user_name: str) -> None:
    """
    Update the username of a user in the database given the user's id.

    Parameters:
        user_id (str): The id of the user whose username is to be updated.
        new_user_name (str): The new username for the user.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_name = %s
        WHERE user_id = %s
    '''    
    cur.execute(send_query, (new_user_name, user_id))

def update_username_endpoint(data, conn):
    data = data["data"]
    user_id = data["user_id"]
    new_user_name = data["new_user_name"]
    try:
        handle_user_name_update(user_id, new_user_name)
        conn.sendall("True".encode("utf-8"))
    except:
        conn.sendall("False".encode("utf-8"))

def handle_user_password_update(user_id: str, new_password: str) -> None:
    """
    Update the password of a user in the database given the user's id.

    Parameters:
        user_id (str): The id of the user whose password is to be updated.
        new_password (str): The new password for the user.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_password = %s
        WHERE user_id = %s
    '''    
    cur.execute(send_query, (new_password, user_id))

def update_password_endpoint(data, conn):
    data = data["data"]
    user_id = data["user_id"]
    new_password = data["new_password"]
    try:
        handle_user_password_update(user_id, new_password)
        conn.sendall("True".encode("utf-8"))
    except:
        conn.sendall("False".encode("utf-8"))    

def handle_user_color_update(user_id: str, new_user_color: str) -> None:
    """
    Update the color of a user in the database given the user's id.

    Parameters:
        user_id (str): The id of the user whose color is to be updated.
        new_user_color (str): The new color for the user.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_color = %s
        WHERE user_id = %s
    '''    
    cur.execute(send_query, (new_user_color, user_id))

def update_color_endpoint(data, conn):
    data = data["data"]
    user_id = data["user_id"]
    new_user_color = data["new_user_color"]
    try:
        handle_user_color_update(user_id, new_user_color)
        conn.sendall("True".encode("utf-8"))
    except:
        conn.sendall("False".encode("utf-8"))

def handle_user_symbol_update(user_id: str, new_user_symbol: str) -> None:
    """
    Update the symbol of a user in the database given the user's id.

    Parameters:
        user_id (str): The id of the user whose symbol is to be updated.
        new_user_symbol (str): The new symbol for the user.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_symbol = %s
        WHERE user_id = %s
    '''    
    cur.execute(send_query, (new_user_symbol, user_id))

def update_symbol_endpoint(data, conn):
    data = data["data"]
    user_id = data["user_id"]
    new_user_symbol = data["new_user_symbol"]
    try:
        handle_user_symbol_update(user_id, new_user_symbol)
        conn.sendall("True".encode("utf-8"))
    except:
        conn.sendall("False".encode("utf-8"))