import psycopg2
from uuid import uuid4

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

def handle_invite_creation(user_id: str, server_id: str, invite_code: str):
    """
        Create an invite for a server in the database.

        Parameters:
            user_id (str): The ID of the user creating the invite.
            server_id (str): The ID of the server for which the invite is created.
            invite_code (str): The unique code for the invite.

        Returns:
            None
    """

    invite_id = str(uuid4())

    send_query = '''
        INSERT into "Discord"."InvitesInfo" (invite_id, server_id, invite_code, invite_creator_id) values (%s, %s, %s, %s)
    '''

    cur.execute(send_query, (invite_id, user_id, server_id, invite_code))   


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
    



