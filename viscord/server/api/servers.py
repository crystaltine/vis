from .db import cur
from uuid import uuid4
import datetime

from .roles import get_server_perms, handle_role_creation
from .members import handle_member_creation, handle_adding_member_roles
from .chats import handle_chat_creation
from .flask_app import app
from .helpers import *
from flask import request, Response
import requests

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

    if not validate_fields(request.json, {"user_id": str, "server_name": str, "server_icon": str, "server_color": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    server_name = request.json["server_name"]
    server_icon = request.json["server_icon"]
    server_color = request.json["server_color"]
    if server_color[0] != "#" or len(server_color) != 7 or set(server_color[1:]).difference(set("0123456789abcdef")):
        return invalid_fields()
    
    
    server_id = str(uuid4())
    server_timestamp = str(datetime.datetime.now())
    # TODO: make this entire try/except block not api
    try:
        send_query = '''
            INSERT into "Discord"."ServerInfo" (server_id, server__name, color, server_icon, server_creation_timestamp) values (%s, %s, %s, %s, %s)
        '''

        cur.execute(send_query, (server_id, server_name, server_color, server_icon, server_timestamp))

        # add the user creating the server to the server as a member
        
        handle_member_creation(user_id, server_id)

        # create an "admin" role for the user creating the server 
        handle_role_creation(server_id, "admin", "#FFD700", "🜲", 0, 0, True, True, True, True, True, True, True)

        # create an "everyone" role for the server (will be assigned to all people in the server)
        handle_role_creation(server_id, "everyone", "#FFFFFF", "🌍", 1, 0, False, False, False, False, False, False, False)

        #assign the "admin" and "everyone" roles to the user creating the server
        handle_adding_member_roles(user_id, server_id, "admin")
        handle_adding_member_roles(user_id, server_id, "everyone")

        # create a general chat for the server
        handle_chat_creation(user_id, server_id, "general", "text chat", "General chat for the server", 0, 0, 0, False)
        return return_success()
    except Exception as e:
        return return_error(e)


def handle_server_name_update(user_id:str, server_id: str, new_server_name: str):
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
    
    perms = get_server_perms(user_id, server_id)

    if not perms["manage_server"]:
        print("You do not have permission to change the server name")
        return

    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET server__name = %s
        WHERE server_id = %s
    '''    
    cur.execute(send_query, (new_server_name, server_id))

def handle_server_color_update(user_id: str, server_id: str, new_color_color: str) -> None:
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

    perms = get_server_perms(user_id, server_id)

    if not perms["manage_server"]:
        print("You do not have permission to change the server color")
        return

    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET color = %s
        WHERE server_id = %s
    '''    

    cur.execute(send_query, (new_color_color, server_id))

def handle_server_icon_update(user_id: str, server_id: str, new_server_icon: str) -> None:
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

    perms = get_server_perms(user_id, server_id)

    if not perms["manage_server"]:
        print("You do not have permission to change the server color")
        return

    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET server_icon = %s
        WHERE server_id = %s
    '''    

    cur.execute(send_query, (new_server_icon, server_id))



def handle_user_leaving_server(user_id: str, server_id: str) -> None:
    """
    Deletes the row from the 'MemberInfo' table to allow the user to leave the server.

    Parameters:
        user_id (str): The ID of the user leaving the server.
        server_id (str): The ID of the server the user is leaving.

    Returns:
        None
    """
    send_query = '''
        DELETE FROM "Discord"."MemberInfo"
        WHERE user_id = %s AND server_id = %s
    '''    

    cur.execute(send_query, (user_id, server_id))

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

