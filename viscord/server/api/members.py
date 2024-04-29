from .db import cur
import datetime
from .flask_app import app
from .helpers import *
from flask import request, Response
from uuid import uuid4

@app.route("/api/members/create", methods=["POST"])
def handle_member_creation():
    
    if not validate_fields(request.json, {"user_id": str, "server_id": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]

    try:

        member_join_date = str(datetime.datetime.now())

        send_query = '''
            INSERT into "Discord"."MemberInfo" (member_id, user_id, server_id, member_join_date) values (%s, %s, %s)
        '''

        cur.execute(send_query, (uuid4(), user_id, server_id, member_join_date))

        return return_success()
    except Exception as e:
        return return_error(e)
    

@app.route("/api/members/add_role", methods=["POST"])
def handle_adding_member_roles():
    if not validate_fields(request.json, {"user_id": str, "server_id": str, "role_id": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    role_id = request.json["role_id"]

    try:
        
        send_query = '''
            SELECT COUNT(*) FROM "Discord"rsInfo" 
            WHERE user_id = %s AND server_id = %s
        '''

        cur.execute(send_query, (user_id, server_id))

        if cur.fetchone()[0] == 0:
            return return_error(f"Member {user_id} does not exist in server")

        send_query = '''
            SELECT roles_list FROM "Discord"."MembersRoles" 
            WHERE user_id = %s AND server_id = %s
        '''

        cur.execute(send_query, (user_id, server_id))
        current_roles_list = cur.fetchone()[0]

        new_roles_list = current_roles_list + role_id

        send_query = '''
            UPDATE "Discord"."MemberInfo"
            SET roles_list = %s
            WHERE user_id = %s AND server_id = %s
        '''

        cur.execute(send_query, (new_roles_list, user_id, server_id))
        return return_success()
    except Exception as e:
        return return_error(e)

@app.route("/api/members/remove_role", methods=["POST"])
def handle_removing_member_roles():
    if not validate_fields(request.json, {"user_id": str, "server_id": str, "role_id": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    role_id = request.json["role_id"]

    try:
        
        send_query = '''
            SELECT COUNT(*) FROM "Discord"."MemberInfo" 
            WHERE user_id = %s AND server_id = %s
        '''

        cur.execute(send_query, (user_id, server_id))

        if cur.fetchone()[0] == 0:
            return return_error(f"Member {user_id} does not exist in server")

        send_query = '''
            SELECT roles_list FROM "Discord"."MembersRoles" 
            WHERE user_id = %s AND server_id = %s
        '''

        cur.execute(send_query, (user_id, server_id))
        current_roles_list = cur.fetchone()[0]

        #new_roles_list = current_roles_list + role_id
        if role_id not in current_roles_list:
            return return_error(f"Role {role_id} not found in member's roles")
        current_roles_list.remove(role_id)

        send_query = '''
            UPDATE "Discord"."MemberInfo"
            SET roles_list = %s
            WHERE user_id = %s AND server_id = %s
        '''

        cur.execute(send_query, (current_roles_list, user_id, server_id))
        return return_success()
    except Exception as e:
        return return_error(e)



@app.route("/api/members/update_nickname", methods=["POST"])
def update_member_nickname() -> bool:
    """
    @backend: server -> database
    
    Updates the nickname of a member in a server. If the new nickname is empty, their nickname in
    the members table 
    """

    if not validate_fields(request.json, {"user_id": str, "server_id": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    if "new_nickname" in request.json:
        new_nickname = request.json["new_nickname"]
    else:
        new_nickname = ""

    try:
        send_query = """update "Discord"."MemberInfo" set nickname = %s where server_id = %s and user_id = %s"""
        if not new_nickname:
            cur.execute(send_query, (None, server_id, user_id))
        else:
            cur.execute(send_query, (new_nickname, server_id, user_id))
        return return_success()
    except Exception as e:
        return return_error(e)

@app.route("/api/members/update_nickname_color", methods=["POST"])
def update_nick_color() -> bool:
    """
    @backend: server -> database
    
    Changes the color of a user's nickname in a server. If the new color is `None`, null is
    inserted into the database, but this should be interpreted as something like white by the client.
    """

    if not validate_fields(request.json, {"user_id": str, "server_id": str, "new_color": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]
    new_color = request.json["new_color"]

    if new_color[0] != "#" or len(new_color) != 7 or set(new_color[1:]).difference(set("0123456789abcdef")):
        return invalid_fields()
    
    try:
        send_query = """update "Discord"."MemberInfo" set nick_color = %s where server_id = %s and user_id = %s """
        cur.execute(send_query, (new_color, server_id, user_id))
        return return_success()
    except Exception as e:
        return return_error(e)
    
@app.route("/api/members/leave_server", methods=["POST"])
def handle_user_leaving_server() -> None:
    """
    Deletes the row from the 'MemberInfo' table to allow the user to leave the server.

    Parameters:
        user_id (str): The ID of the user leaving the server.
        server_id (str): The ID of the server the user is leaving.

    Returns:
        None
    """

    if not validate_fields(request.json, {"user_id": str, "server_id": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    server_id = request.json["server_id"]

    send_query = '''
        DELETE FROM "Discord"."MemberInfo"
        WHERE user_id = %s AND server_id = %s
    '''    
    try:
        cur.execute(send_query, (user_id, server_id))
        return return_success()
    except Exception as e:
        return return_error(e)