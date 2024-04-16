from typing import Literal

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

# THIS IS TEMPORARY - we will have an imported `cur` variable in every file
def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()


def change_username(user_id: str, new_username: str) -> Literal["success", "failure", "unavailable"]:
    """
    Change the username of a user in the database. Provide the user's unique ID and the new username.
    
    Usernames must be unique, this function will check.

    Returns `success` if username changed successfully, `failure` if database error, `unavailable` if name was taken.
    """

    try:
        send_query = '''select user_name FROM "Discord"."UserInfo" where (user_name = %s)'''
        cur.execute(send_query, (new_username))
        data = cur.fetchall()
        
        if len(data) == 0: # if len is 0, then nobody has that username
            send_query = '''insert into "Discord"."UserInfo" (user_name = %s) where (user_id = %s)'''
            cur.execute(send_query, (new_username, user_id))
            return "success"
        else: # name taken
            return "unavailable"
    except:
        return "failure"

def change_user_password(user_id: str, new_password: str) -> Literal["success", "failure"]:
    """
    Change a password given the user id. Returns strings `success` or `failure`.
    """
    try:
        send_query = '''insert into "Discord"."UserInfo" (user_password) values (%s) where (user_id = %s)'''
        cur.execute(send_query, (new_password, user_id))
        return 'success'
    except:
        return 'failure'
        

def change_user_color(user_id: str, color: str) -> Literal["success", "failure"]:
    """
    Change a user's name color (hex) given the user id. Returns strings `success` or `failure`. 
    """
    try:
        send_query = '''update "Discord"."UserInfo" (user_color = %s) where (user_id = %s)'''
        cur.execute(send_query, (color, user_id))
        return 'success'
    except: 
        return 'failure'
        
def update_user_symbol(user_id: str, symbol: str) -> Literal["success", "failure"]:
    """
    Change a user's prefix symbol given the user id. Returns strings `success` or `failure`. 
    """
    try:
        send_query = """update "Discord"."UserInfo" set user_symbol = %s where user_name = %s"""
        cur.execute(send_query, (symbol, user_name))
        return 'success'
    except:
        return 'failure'

def get_user_servers(user_id):
    """
    Retrieves the servers that the given user has activel

    Parameters:
        user_id (str): String containing the "user_id" of the user

    Returns:
        list
    """
    try:
        send_query = """select * from "Discord"."MemberInfo" where user_id = %s""" #grabs all member data for the user_id
        cur.execute(send_query, (user_id,))
        records = cur.fetchall()
        servers = []
        for x in len(records):
            servers.append(records[x][1]) #stores all the servers that the user is a member of
        return servers
    except:
        return []