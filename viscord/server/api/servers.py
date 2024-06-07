from .db import cur
from uuid import uuid4
import datetime

from .flask_app import app
from .helpers import *
from flask import request, Response
import requests
from .server_config import URI

@app.route("/api/servers/create", methods=["POST"])
def handle_server_creation() -> None:
    """
    Create a new server in the database along with necessary initial setup.

    Parameters:
        user_id (str): The ID of the user creating the server.
        server_name (str): The name of the server.
        server_icon (str): The icon of the server.
        server_color (str): The color of the server (hex code).

    Returns:
        None

    This method performs the following steps for initializing a new server:
    1. Generates a unique server ID.
    2. Inserts server information into the database including its name, icon, color, and creation timestamp.
    3. Creates a general chat for the server with default settings.
    4. Creates an "admin" role for the user creating the server with full permissions.
    5. Creates an "everyone" role for the server that will be assigned to all members.
    6. Adds the user creating the server as a member of the server.
    7. Assigns the "admin" and "everyone" roles to the user creating the server.
    """

    if not validate_fields(request.json, {"user_token": str, "server_name": str, "server_icon": str, "server_color": str}):
        return invalid_fields()
    
    user_token = request.json["user_token"]
    if not is_valid_token(user_token):
        return forbidden()
    user_id = get_user_id(user_token)
    server_name = request.json["server_name"]
    server_icon = request.json["server_icon"]
    server_color = request.json["server_color"]
    if not validate_color(server_color):
        return invalid_fields()
    
    
    server_id = str(uuid4())
    server_timestamp = str(datetime.datetime.now())
    # TODO: make this entire try/except block not api
    try:
        send_query = '''
            INSERT into "Discord"."ServerInfo" (server_id, server__name, color, server_icon, server_creation_timestamp, server_owner) values (%s, %s, %s, %s, %s, %s)
        '''

        cur.execute(send_query, (server_id, server_name, server_color, server_icon, server_timestamp, user_id))

        # add the user creating the server to the server as a member

        send_query = """insert into "Discord"."MemberInfo" (member_id, user_id, server_id, member_join_date) values (%s, %s, %s, %s)"""
        member_timestamp = str(datetime.datetime.now()) #timestamp
        member_id = str(uuid4()) #unique member id
        cur.execute(send_query, (member_id, user_id, server_id, member_timestamp))
        

        # create an "admin" role for the user creating the server 
        data = {
            "server_id": server_id,
            "role_name": "admin",
            "role_color": "#FFD700",
            "role_symbol": "🜲",
            "priority": 0,
            "permissions": 0,
            "manage_server": True,
            "manage_chats": True,
            "manage_members": True,
            "manage_roles": True,
            "manage_voice": True,
            "manage_messages": True,
            "is_admin": True
        }

        #handle_role_creation(server_id, "admin", "#FFD700", "🜲", 0, 0, True, True, True, True, True, True, True)
        resp = requests.post(URI + "/api/roles/create_role", json=data)
        if resp.status_code != 200:
            return return_error("Failed to create admin role")
        
        admin_role_id = resp.json()["role_id"]
        print(admin_role_id)

        data = {
            "server_id": server_id,
            "role_name": "everyone",
            "role_color": "#FFFFFF",
            "role_symbol": "🌍",
            "priority": 1,
            "permissions": 0,
            "manage_server": False,
            "manage_chats": False,
            "manage_members": False,
            "manage_roles": False,
            "manage_voice": False,
            "manage_messages": False,
            "is_admin": False,
            "id_override": "everyone"
        }

        # create an "everyone" role for the server (will be assigned to all people in the server)
        #handle_role_creation(server_id, "everyone", "#FFFFFF", "🌍", 1, 0, False, False, False, False, False, False, False)

        resp = requests.post(URI + "/api/roles/create_role", json=data)
        if resp.status_code != 200:
            return return_error("Failed to create admin role")

        data = {
            "user_token": str(user_token),
            "server_id": str(server_id),
            "role_id": str(admin_role_id)
        }

        resp = requests.post(URI + "/api/members/add_role", json=data)
        if resp.status_code != 200:
            return return_error("Failed to add admin role to user")
        
        data = {
            "user_token": str(user_token),
            "server_id": str(server_id),
            "role_id": str(server_id) + "_" + "everyone"
        }

        resp = requests.post(URI + "/api/members/add_role", json=data)
        if resp.status_code != 200:
            return return_error("Failed to add everyone role to user")

        #assign the "admin" and "everyone" roles to the user creating the server
        # handle_adding_member_roles(user_id, server_id, "admin")
        # handle_adding_member_roles(user_id, server_id, "everyone")

        # create a general chat for the server
        
        data = {
            "user_token": user_token,
            "server_id": server_id,
            "chat_name": "general",
            "chat_type": "text chat",
            "chat_topic": "General chat for the server",
            "chat_order": 0,
            "read_perm_level": 0,
            "write_perm_level": 0,
            "is_dm": False
        }

        resp = requests.post(URI + "/api/chats/create", json=data)
        if resp.status_code != 200:
            return return_error("Failed to create general chat")
        
        data = {
            "type": "success",
            "server_id": server_id
        }

        # handle_chat_creation(user_id, server_id, "general", "text chat", "General chat for the server", 0, 0, 0, False)
        return Response(json.dumps(data), status=200)
    except Exception as e:
        return return_error(e)


@app.route("/api/servers/update_name", methods=["POST"])
def handle_server_name_update():
    """
    Update the name of a server in the database given the server's id. It first checks whether
    the user making the request has the necessary permissions to manage the server. If the user does not have
    permission, it prints a message indicating so and returns without updating the database.

    Parameters:
        user_id (str): The id of the user making the request.
        server_id (str): The id of the server whose name is to be updated.
        new_server_name (str): The new name for the server.

    Returns:
        None
    """
    
    if not validate_fields(request.json, {"user_token": str, "server_id": str, "new_server_name": str}):
        return invalid_fields()
    
    user_token = request.json["user_token"]
    if not is_valid_token(user_token):
        return forbidden()
    user_id = get_user_id(user_token)
    server_id = request.json["server_id"]
    new_server_name = request.json["new_server_name"]


    
    data = {
        "user_token": user_token,
        "server_id": server_id
    }
    resp = requests.post(URI + "/api/members/get_perms", json=data)
    if resp.status_code != 200:
        return return_error("Failed to get server permissions")
    perms = resp.json()

    if not perms["manage_server"]:
        return missing_permissions()

    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET server__name = %s
        WHERE server_id = %s
    '''    
    try:
        cur.execute(send_query, (new_server_name, server_id))
        return return_success()
    except Exception as e:
        return return_error(e)

@app.route("/api/servers/update_color", methods=["POST"])
def handle_server_color_update() -> None:
    """
    Update the color of a server in the database given the server's id. It first checks whether
    the user making the request has the necessary permissions to manage the server. If the user does not have
    permission, it prints a message indicating so and returns without updating the database.

    Parameters:
        user_id (str): The id of the user making the request.
        server_id (str): The id of the server whose color is to be updated.
        new_color_color (str): The new color for the server.

    Returns:
        None
    """

    if not validate_fields(request.json, {"user_token": str, "server_id": str, "new_color": str}):
        return invalid_fields()
    
    user_token = request.json["user_token"]
    if not is_valid_token(user_token):
        return forbidden()
    user_id = get_user_id(user_token)
    server_id = request.json["server_id"]
    new_color = request.json["new_color"]
    if not validate_color(new_color):
        return invalid_fields()

    data = {
        "user_token": user_token,
        "server_id": server_id
    }
    resp = requests.post(URI + "/api/members/get_perms", json=data)
    if resp.status_code != 200:
        return return_error("Failed to get server permissions")
    perms = resp.json()

    if not perms["manage_server"]:
        return missing_permissions()

    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET color = %s
        WHERE server_id = %s
    '''    

    try:
        cur.execute(send_query, (new_color, server_id))
        return return_success()
    except Exception as e:
        return return_error(e)
    
@app.route("/api/servers/server_info", methods=["POST"])
def get_server_info() -> Response:
    """
    Get information about a server given the server's id.

    Parameters:
        server_id (str): The id of the server whose information is to be retrieved.

    Returns:
        Response: A response containing the server's name, icon, color, and creation timestamp.
    """

    if not validate_fields(request.json, {"server_id": str}):
        return invalid_fields()
    
    server_id = request.json["server_id"]

    send_query = '''
        SELECT server__name, server_icon, color, server_creation_timestamp
        FROM "Discord"."ServerInfo"
        WHERE server_id = %s
    '''

    try:
        cur.execute(send_query, (server_id,))
        server_info = cur.fetchone()
        if server_info is None:
            return return_error("Server not found")
        resp = {
            "server_name": server_info[0],
            "server_icon": server_info[1],
            "color": server_info[2],
            "server_creation_timestamp": str(server_info[3])
        }
        return Response(json.dumps({
            "type": "success",
            "data": resp
        }, default=str), status=200)
    except Exception as e:
        return return_error(e)

@app.route("/api/servers/update_icon", methods=["POST"])
def handle_server_icon_update() -> None:
    """
    Update the icon of a server in the database given the server's id. It first checks whether
    the user making the request has the necessary permissions to manage the server. If the user does not have
    permission, it prints a message indicating so and returns without updating the database.

    Parameters:
        user_id (str): The id of the user making the request.
        server_id (str): The id of the server whose icon is to be updated.
        new_server_icon (str): The new icon for the server.

    Returns:
        None
    """

    if not validate_fields(request.json, {"user_token": str, "server_id": str, "new_server_icon": str}):
        return invalid_fields()
    
    user_token = request.json["user_token"]
    if not is_valid_token(user_token):
        return forbidden()
    user_id = get_user_id(user_token)
    server_id = request.json["server_id"]
    new_server_icon = request.json["new_server_icon"]

    data = {
        "user_token": user_token,
        "server_id": server_id
    }
    resp = requests.post(URI + "/api/members/get_perms", json=data)
    if resp.status_code != 200:
        return return_error("Failed to get server permissions")
    perms = resp.json()

    if not perms["manage_server"]:
        return missing_permissions()

    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET server_icon = %s
        WHERE server_id = %s
    '''    

    try:
        cur.execute(send_query, (new_server_icon, server_id))
        return return_success()
    except Exception as e:
        return return_error(e)


@app.route("/api/servers/get_chats", methods=["POST"])
def get_server_chats() -> Response:
    """
    Get all chats for a server given the server's id.

    Parameters:
        server_id (str): The id of the server whose chats are to be retrieved.

    Returns:
        Response: A response containing the server's chats.
    """

    if not validate_fields(request.json, {"server_id": str}):
        return invalid_fields()
    
    server_id = request.json["server_id"]

    send_query = '''
        SELECT chat_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm
        FROM "Discord"."ChatInfo"
        WHERE server_id = %s
    '''

    try:
        cur.execute(send_query, (server_id,))
        chats = cur.fetchall()
        resp = []
        for chat in chats:
            resp.append({
                "chat_id": chat[0],
                "chat_name": chat[1],
                "chat_type": chat[2],
                "chat_topic": chat[3],
                "chat_order": chat[4],
                "read_perm_level": chat[5],
                "write_perm_level": chat[6],
                "is_dm": chat[7]
            })
        return Response(json.dumps({
            "type": "success",
            "data": resp
        }, default=str), status=200)
    except Exception as e:
        return return_error(e)



def db_on_join_server(user_id: str, server_id: str):
    """
    Creates a MemberInfo row within the database based on the given user and server.

    Parameters:
        user_id (str): String containing the "user_id" of the user that is joining the specified server.
        server_id (str): String containing the "server_id" of the server that the specified user is joining.

    Returns:
        None
    """
    try:
        send_query = """insert into "Discord"."MemberInfo" (member_id, user_id, server_id, member_join_date) values (%s, %s, %s, %s)"""
        member_timestamp = str(datetime.datetime.now()) #timestamp
        member_id = str(uuid4()) #unique member id
        cur.execute(send_query, (member_id, user_id, server_id, member_timestamp))
        return True
    except:
        return False
    
def get_server_chats(server_id):
    try:
        send_query = """select * from "Discord"."ChatInfo" where server_id = %s""" #grabs all chat data for the server_id
        cur.execute(send_query, (server_id,))
        records = cur.fetchall()
        chats = []
        for x in len(records):
            chats.append(records[x][2])
        return chats
    except:
        return []

