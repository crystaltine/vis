import psycopg2
from uuid import uuid4
import datetime

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

def handle_member_creation(user_id: str, server_id: str):
    member_join_date = str(datetime.datetime.now())

    send_query = '''
        INSERT into "Discord"."MembersInfo" (member_id, server_id, member_join_date) values (%s, %s, %s)
    '''

    cur.execute(send_query, (user_id, server_id, member_join_date))



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