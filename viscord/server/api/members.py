from .db import cur
import datetime

def handle_member_creation(user_id: str, server_id: str):
    member_join_date = str(datetime.datetime.now())

    send_query = '''
        INSERT into "Discord"."MembersInfo" (member_id, server_id, member_join_date) values (%s, %s, %s)
    '''

    cur.execute(send_query, (user_id, server_id, member_join_date))

def member_creation_endpoint(data, conn):
    user_id = data["data"]["user_id"]
    server_id = data["data"]["server_id"]
    try:
        handle_member_creation(user_id, server_id)
        conn.sendall("True".encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))


def handle_adding_member_roles(user_id: str, server_id: str, role_id: str):
    send_query = '''
        SELECT COUNT(*) FROM "Discord"."MembersInfo" 
        WHERE user_id = %s AND server_id = %s
    '''

    cur.execute(send_query, (user_id, server_id))

    if cur.fetchone()[0] == 0:
        print("Member does not exist in server")
        return

    send_query = '''
        SELECT roles_list FROM "Discord"."MembersRoles" 
        WHERE user_id = %s AND server_id = %s
    '''

    cur.execute(send_query, (user_id, server_id))
    current_roles_list = cur.fetchone()[0]

    new_roles_list = current_roles_list + role_id

    send_query = '''
        UPDATE "Discord"."MembersInfo"
        SET roles_list = %s
        WHERE user_id = %s AND server_id = %s
    '''

    cur.execute(send_query, (new_roles_list, user_id, server_id))

def add_member_roles_endpoint(data, conn):
    user_id = data["data"]["user_id"]
    server_id = data["data"]["server_id"]
    role_id = data["data"]["role_id"]
    try:
        handle_adding_member_roles(user_id, server_id, role_id)
        conn.sendall("True".encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))

def update_member_nickname(user_id: str, server_id: str, new_nickname: str = "") -> bool:
    """
    @backend: server -> database
    
    Updates the nickname of a member in a server. If the new nickname is empty, their nickname in
    the members table 
    """
    send_query = """update "Discord"."MemberInfo" set nickname = %s where server_id = %s and user_id = %s"""
    if not new_nickname:
        cur.execute(send_query, (None, server_id, user_id))
    else:
        cur.execute(send_query, (new_nickname, server_id, user_id))

def update_member_nickname_endpoint(data, conn):
    user_id = data["data"]["user_id"]
    server_id = data["data"]["server_id"]
    new_nickname = data["data"]["new_nickname"]
    try:
        update_member_nickname(user_id, server_id, new_nickname)
        conn.sendall("True".encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))

def update_nick_color(user_id: str, server_id: str, new_color: str | None) -> bool:
    """
    @backend: server -> database
    
    Changes the color of a user's nickname in a server. If the new color is `None`, null is
    inserted into the database, but this should be interpreted as something like white by the client.
    """
    send_query = """update "Discord" . "MemberInfo" set nick_color = %s where server_id = %s and user_id = %s """ 
    cur.execute(send_query, (new_color, server_id, user_id))

def update_nick_color_endpoint(data, conn):
    user_id = data["data"]["user_id"]
    server_id = data["data"]["server_id"]
    new_color = data["data"]["new_color"]
    try:
        update_nick_color(user_id, server_id, new_color)
        conn.sendall("True".encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))