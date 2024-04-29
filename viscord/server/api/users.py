import datetime
from .db import cur
from typing import Literal
from uuid import uuid4
from json import dumps
import random
from .helpers import *
from .flask_app import app
from flask import request, Response
import requests
from .server_config import URI

@app.route("/api/users/create", methods=["POST"])
def create_user() -> Literal["success", "false", "username-unavailable"]:
    """
    Creates an entry in the users table for this new user.

    Returns 'username-unavailable' if username is already taken.
    """
    
    if not validate_fields(request.json, {"user_id": str, "username": str, "password": str, "color": str, "symbol": str}):
        return invalid_fields()

    user_id = request.json["user_id"]
    username = request.json["username"]
    password = request.json["password"]
    color = request.json["color"]
    symbol = request.json["symbol"]

    if not username_available(username):
        return return_error(f"Username {username} is already taken")

    send_query='''
    insert into "Discord"."UserInfo" 
    (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) 
    values (%s, %s, %s, %s, %s, %s)
    '''
    try:
        cur.execute(send_query, (user_id, username, password, color, symbol, datetime.datetime.now()))
        return return_success()
    except Exception as e:
        return return_error(e)

@app.route("/api/users/check_username", methods=["POST"])
def username_available() -> bool:
    """
    Returns True if the username hasnt been taken yet, else false.
    """
    if not validate_fields(request.json, {"username": str}):
        return invalid_fields()
    
    username = request.json["username"]

    send_query = """select 1 from "Discord"."UserInfo" where user_name = %s"""
    try:
        cur.execute(send_query, (username,)) # weird tuple hack
        records = cur.fetchall()
        data = {"available": len(records) == 0}
        return Response(dumps(data), status=200, mimetype="application/json")
    except Exception as e:
        return return_error(e)

@app.route("/api/users/change_username", methods=["POST"])
def change_username() -> Literal["success", "failure", "unavailable"]:
    """
    Update the username of a user in the database given the user's id.

    Returns 'unavailable' if the name is already taken.
    """
    
    if not validate_fields(request.json, {"user_id": str, "new_username": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    new_username = request.json["new_username"]

    resp = requests.post(URI + "/api/users/check_username", json={"username": request.json["new_username"]})
    if resp.status_code != 200:
        return return_error("Failed to check username availability")
    if not resp.json()["available"]:
        return return_error("Username is already taken")
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_name = %s
        WHERE user_id = %s
    '''    
    try:
        cur.execute(send_query, (new_username, user_id))
        return return_success()
    except Exception as e:
        return return_error(e)

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