import psycopg2
import datetime
import random
from uuid import uuid4
from typing import Optional, Dict

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

def get_server_perms(user_id:str, server_id: str):
    member_query="""select roles_list from "Discord"."MemberInfo" where user_id = %s and server_id= %s"""
    cur.execute(member_query, (user_id, server_id))
    roles_list= cur.fetchall()[0][0]

    perms={"manage_server":False, "manage_chats":False, "manage_members":False, "manage_roles":False, "manage_voice":False,  
           "manage_messages":False, "is_admin":False}
    list_perms=list(perms.items())

    # Getting all the perms based on the list of roles and updating the dict (which combines all the perms of all the roles the user has)

    for role_id in roles_list:
        perm_query="""select manage_server, manage_chats, manage_members, manage_roles, manage_voice, manage_messages, is_admin from "Discord"."RolesInfo" where role_id = %s"""
        cur.execute(perm_query, (role_id,))
        perm_arr=cur.fetchall()[0]
        
        # Checking to see if a role has a permission that isn't already true in the dict

        for i in range(0,len(perm_arr)):
            if not perms[list_perms[i][0]] and perm_arr[i]:
                perms[list_perms[i][0]]=True
    
    # If the user is an admin, all perms should be true

    if perms["is_admin"]:
        for key in perms:
            perms[key]=True
    
    return perms

def handle_server_creation(data: Optional[Dict[str, str]]) -> None:
    """
    Create a server in the database with given data.

    If any parts of the data are None, it will still create a server with preset information.

    Parameters:
        data (Optional[Dict[str, str]]): Dictionary containing keys "server_name", "server_symbol", and "server_color".
            If None, a test server with preset information will be created. Default values for missing keys:
            - "server_name": "test_server"
            - "server_symbol": random choice from symbols "☀☁★☾♥♠♦♣♫☘☉☠"
            - "server_color": "#ffffff"

    Returns:
        None
    """
    
    server_id = str(uuid4())
    print("Server ID: " + server_id)
    server_timestamp = str(datetime.datetime.now())
    if data is None:
        server_name = "test_server"
        server_icon = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
        server_color = "#ffffff"
    else:
        server_name = data.get("server_name", "test_server")
        server_icon = data.get("server_symbol", random.choice("☀☁★☾♥♠♦♣♫☘☉☠"))
        server_color = data.get("server_color", "#ffffff")

    send_query = '''
        INSERT into "Discord"."ServerInfo" (server_id, server__name, color, server_icon, server_creation_timestamp) values (%s, %s, %s, %s, %s)
    '''

    cur.execute(send_query, (server_id, server_name, server_color, server_icon, server_timestamp))

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
    # Assuming `cur` is a valid cursor object from psycopg2
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
    # Assuming `cur` is a valid cursor object from psycopg2
    cur.execute(send_query, (new_server_icon, server_id))

def test_retrieve_server_information(server_id: str) -> None:
    """
    Test command to retrieve information about a server.

    Parameters:
        server_id (str): The id of the server to retrieve information for.

    Returns:
        None
    """
    send_query = '''
        SELECT * FROM "Discord"."ServerInfo"
        WHERE server_id = %s
    '''
    # Assuming `cur` is a valid cursor object from psycopg2
    cur.execute(send_query, (server_id,))
    records = cur.fetchall()
    if records:
        print("Server Information:")
        for result in records:
            print("Server ID:", result[0])
            print("Server Name:", result[1])
            print("Server Color:", result[2])
            print("Server Icon:", result[3])
            print("Server Creation Timestamp:", result[4])
            print("--------------------------------")
    else:
        print("Server not found")


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

#handles a new user joining a server
def handle_user_joining_server():
    pass

handle_server_creation(None)
server_id = input("Enter server id: ")
test_retrieve_server_information(server_id)
print()
print("Updating user name...")
print()
handle_server_name_update(server_id, "NEWNAME")
print()
print("Updating server color...")
print()
handle_server_color_update(server_id, "#000000")
print()
print("Updating server icon...")
print()
handle_server_icon_update(server_id, "☉")
test_retrieve_server_information(server_id)




