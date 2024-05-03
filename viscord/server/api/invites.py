from uuid import uuid4
from .db import cur
from .roles import get_server_perms
from .flask_app import app
from .helpers import *
from flask import request, Response
import requests
from .server_config import URI
import datetime

def handle_invite_creation(user_id, server_id, invite_code):
    """
        Create an invite for a server in the database.

        Parameters:
            user_id (str): The ID of the user creating the invite.
            server_id (str): The ID of the server for which the invite is created.
            invite_code (str): The unique code for the invite.

        Returns:
            None
    """

    try:

        invite_id = str(uuid4())

        send_query = '''
            INSERT into "Discord"."InvitesInfo" (invite_id, server_id, invite_code, invite_creator_id) values (%s, %s, %s, %s)
        '''

        cur.execute(send_query, (invite_id, user_id, server_id, invite_code))   
        return True, invite_id
    except Exception as e:
        return False, str(e)

# NO API
def handle_check_existing_invite(server_id: str) -> str:
    """
        Check if there is an existing invite for a server.

        Parameters:
            server_id (str): The ID of the server for which the invite is checked.

        Returns:
            str: The invite code if an invite exists, else None.
    """

    send_query = '''
        SELECT invite_code from "Discord"."InvitesInfo" where server_id = %s
    '''

    cur.execute(send_query, (server_id,))

    invite_code = cur.fetchone()
    
    if invite_code:
        return invite_code[0]
    return None

# NO API
# will find server_id that invite code corresponds to, if none exists return None
def handle_join_code_validation(invite_code: str) -> str:
    """
        Finds the server ID the invite code entered by the user corresponds with.

        Parameters:
            invite_code (str): The invite code entered by the user.

        Returns:
            str: The server ID if the invite code is valid, else None.
    """

    send_query = '''
        SELECT server_id from "Discord"."InvitesInfo" where invite_code = %s
    '''

    cur.execute(send_query, (invite_code,))

    server_id = cur.fetchone()
    
    if server_id:
        return server_id[0]
    return None
    
@app.route("/api/invites/create", methods=["POST"])
def handle_server_invite_request() -> str:
    """
        Create an invite for a server in the database. This method first checks if the user making the request 
        has the necessary permissions to create an invite for the server. If the user does not have permission, 
        it prints a message indicating so and returns without creating an invite. If an invite already exists 
        for the server, it returns the existing invite code. If no invite exists, it creates a new invite code 
        and returns it.

        Parameters:
            user_id (str): The ID of the user creating the invite.
            server_id (str): The ID of the server for which the invite is created.

        Returns:
            str: The invite code for the server.
    """

    # check if user is allowed to create this invite

    if not validate_fields(request.json, {"user_token": str, "server_id": str}):
        return invalid_fields()
    
    user_token = request.json["user_token"]
    if not is_valid_token(user_token):
        return forbidden()
    user_id = get_user_id(user_token)
    server_id = request.json["server_id"]

    data = {"user_id": user_id, "server_id": server_id}
    resp = requests.post(URI + "/api/roles/get_server_perms", json=data)
    if resp.status_code != 200:
        return return_error("Failed to retrieve role permissions")
    perms = resp.json()

    if perms['manage_server'] == False:
        return missing_permissions()

    try:
        # check if there is an existing invite for this server

        existing_invite = handle_check_existing_invite(server_id)

        # if there is an existing invite, return it

        code = ""

        if existing_invite:
            code = existing_invite
        else:
            code = str(uuid4())[:6]
            status, _id = handle_invite_creation(user_id, server_id, code)
            if not status:
                return return_error(_id)
        return Response(json.dumps({"type": "success", "invite_code": code}), status=200)
    except Exception as e:
        return return_error(e)


# will check join code user enters and if its valid add them to the server
@app.route("/api/invites/join", methods=["POST"])
def handle_user_joining_server():
    """
        Handle the process of a user joining a server. First checks if the invite code entered by the user is valid.
        If the invite code is valid, it adds the user to the server. If the invite code is invalid, it prints a message
        indicating so and returns without adding the user to the server.

        Parameters:
            user_id (str): The ID of the user joining the server.
            invite_code (str): The invite code entered by the user.

        Returns:
            None
    """
    
    if not validate_fields(request.json, {"user_token": str, "invite_code": str}):
        return invalid_fields()
    
    user_token = request.json["user_token"]
    if not is_valid_token(user_token):
        return forbidden()
    user_id = get_user_id(user_token)
    invite_code = request.json["invite_code"]

    try:
        server_id =  handle_join_code_validation(invite_code)

        if server_id:

            member_join_date = str(datetime.datetime.now())

            send_query = '''
                INSERT into "Discord"."MemberInfo" (member_id, user_id, server_id, member_join_date) values (%s, %s, %s)
            '''

            cur.execute(send_query, (uuid4(), user_id, server_id, member_join_date))

            data = {
                "user_token": user_token,
                "server_id": server_id,
                "role_id": "everyone"
            }

            response = requests.post(URI + "/api/members/add_role", json={"data": data})
            if response.status_code != 200:
                return Response(json.dumps({"type": "failure", "message": "Joined server; failed to add base role"}), status=400)
            return return_success()
            
        else:
            return Response(json.dumps({"type": "incorrect", "message": "Invalid invite code"}), status=400)
    except Exception as e:
        return return_error(e)