import datetime
from .db import cur
from typing import Literal
from logger import Logger
from uuid import uuid4
from json import dumps
import random

def create_user(user_id: str, username: str, password: str, color: str, symbol: str) -> Literal["success", "false", "username-unavailable"]:
    """
    Creates an entry in the users table for this new user.

    Returns 'username-unavailable' if username is already taken.
    """

    if not username_available(username):
        return 'username-unavailable'

    send_query='''
    insert into "Discord"."UserInfo" 
    (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) 
    values (%s, %s, %s, %s, %s, %s)
    '''
    try:
        cur.execute(send_query, (user_id, username, password, color, symbol, datetime.datetime.now()))
        return 'success'
    except Exception as e:
        Logger.err(f"failed to create user in db: {e}", 'create_user')
        return 'failure'

def handle_create_account(data, conn):
    account_data = data["data"] # {"user": str (username), "password": str (password HASH)}
    
    uuid = str(uuid4())
    symbol = account_data['symbol']
    color = account_data['color']
    username = account_data["username"]
    password = account_data["password"]

    result = create_user(uuid, username, password, color, symbol)

    # TODO - auto-log them in for creating an account
    # needs to use the generated uuid to create a cookie or whatever.
    if result == 'success': conn.sendall("True".encode("utf-8"))
    elif result == 'username-unavailable': conn.sendall("unavailable".encode("utf-8"))
    else: conn.sendall("False".encode("utf-8"))

def username_available(username: str) -> bool:
    """
    Returns True if the username hasnt been taken yet, else false.
    """
    send_query = """select 1 from "Discord"."UserInfo" where user_name = %s"""
    cur.execute(send_query, (username,)) # weird tuple hack
    records = cur.fetchall()
    return len(records) == 0

def change_username(user_id: str, new_username: str) -> Literal["success", "failure", "unavailable"]:
    """
    Update the username of a user in the database given the user's id.

    Returns 'unavailable' if the name is already taken.
    """

    if not username_available(new_username):
        return 'unavailable'

    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_name = %s
        WHERE user_id = %s
    '''    
    try:
        cur.execute(send_query, (new_username, user_id))
        return 'success'
    except Exception as e:
        Logger.err(f"failed to change username: {e}", 'change_username')
        return 'failure'

def handle_change_username(data, conn):
    data = data["data"]
    user_id = data["user_id"]
    new_user_name = data["new_user_name"]

    result = change_username(user_id, new_user_name)
    if result == 'success': conn.sendall("True".encode("utf-8"))
    elif result == 'unavailable': conn.sendall("unavailable".encode("utf-8"))
    else: conn.sendall("False".encode("utf-8"))

def change_password(user_id: str, new_password: str) -> Literal['success', 'failure']:
    """
    Update the password of a user in the database given the user's id.
    NOTE: we are assuming the password already has necessary security measures applied
    (such as salting and hashing)

    Returns 'success'/'failure'
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_password = %s
        WHERE user_id = %s
    '''    
    try:
        cur.execute(send_query, (new_password, user_id))
        return 'success'
    except Exception as e:
        Logger.err(f"failed to change password: {e}", 'change_password')
        return 'failure'

def handle_change_password(data, conn):
    data = data["data"]
    user_id = data["user_id"]
    new_password = data["new_password"]
    
    result = change_password(user_id, new_password)
    if result == 'success': conn.sendall("True".encode("utf-8"))
    else: conn.sendall("False".encode("utf-8"))    

def change_user_color(user_id: str, new_color: str) -> None:
    """
    Update a user's name color in the db.

    Specify color as a hex string or something.

    Returns 'success'/'failure'
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_color = %s
        WHERE user_id = %s
    '''    
    try:
        cur.execute(send_query, (new_color, user_id))
        return 'success'
    except Exception as e:
        Logger.err(f"failed to change user color: {e}", 'change_user_color')
        return 'failure'

def handle_change_user_color(data, conn):
    data = data["data"]
    user_id = data["user_id"]
    new_user_color = data["new_user_color"]

    result = change_user_color(user_id, new_user_color)
    if result == 'success': conn.sendall("True".encode("utf-8"))
    else: conn.sendall("False".encode("utf-8"))  

def change_user_symbol(user_id: str, new_symbol: str) -> None:
    """
    Update the symbol of a user in the database given the user's id.

    `new_symbol` should be a character of the new symbol they chose.

    Returns 'success'/'failure'.
    """

    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_symbol = %s
        WHERE user_id = %s
    '''    
    try:
        cur.execute(send_query, (new_symbol, user_id))
        return 'success'
    except Exception as e:
        Logger.err(f"failed to change user symbol: {e}", 'change_user_symbol')
        return 'failure'

def update_symbol_endpoint(data, conn):
    data = data["data"]
    user_id = data["user_id"]
    new_user_symbol = data["new_user_symbol"]

    result = change_user_color(user_id, new_user_symbol)
    if result == 'success': conn.sendall("True".encode("utf-8"))
    else: conn.sendall("False".encode("utf-8"))  