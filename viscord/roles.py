import psycopg2
from uuid import uuid4

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

def handle_role_creation(server_id: str, role_name: str, role_color: str, role_symbol: str, priority: int, permissions: int, manage_server: bool, manage_chats: bool, manage_members: bool, manage_roles: bool, manage_voice: bool, manage_messages: bool, is_admin: bool):
    role_id = str(uuid4())

    send_query = '''
        INSERT into "Discord"."RolesInfo" (role_id, server_id, role_name, color, role_symbol, priority, permissions, manage_server, manage_chats, manage_members, manage_roles, manage_voice, manage_messages, is_admin) values (%
    '''

    cur.execute(send_query, (role_id, server_id, role_name, role_color, role_symbol, priority, permissions, manage_server, manage_chats, manage_members, manage_roles, manage_voice, manage_messages, is_admin))


