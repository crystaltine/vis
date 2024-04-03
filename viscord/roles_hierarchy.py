from typing import List
from typing import Dict
import psycopg2
from _types import *

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

# Given a user_id, a server_id, and a chat_id, this function will return a dict containing a bool for reading and a bool for writing perms

def get_chat_perms(user_id:str, server_id:str, chat_id:str) -> ChatPerms:
    
    # Stuff for testing- ignore

    # user_id='b98757df-71aa-4615-8345-26c71cfbb304'
    # server_id='ad3f1cd8-ffcd-48ca-abc7-9409c17c9122'
    # chat_id='43eef70b-90bb-40c5-8ece-45abf6a55abb'
    
    # Using the chat_id to pull the perm info from ChatInfo

    chat_query="""select read_perm_level, write_perm_level from "Discord"."ChatInfo" where chat_id = %s"""
    cur.execute(chat_query, (chat_id,))
    perms= cur.fetchall()[0]
    minimum_reading_level, minimum_writing_level=perms[0], perms[1]

    # Getting the user's roles from MemberInfo with the user_id and the server_id

    member_query="""select roles_list from "Discord"."MemberInfo" where user_id = %s and server_id= %s"""
    cur.execute(member_query, (user_id, server_id))
    roles_list= cur.fetchall()[0][0]

    # Getting the highest perm level for all the user's roles

    highest_perm_level=0
    for role_id in roles_list:
        perm_query="""select permissions from "Discord"."RolesInfo" where role_id = %s"""
        cur.execute(perm_query, (role_id,))
        perm_level=int(cur.fetchall()[0][0])

        if perm_level>highest_perm_level:
            highest_perm_level=perm_level
    
    # Checking to see if user's highest perm level >= the needed perm level to read/write

    readable=False
    writeable=False
    if highest_perm_level>=minimum_reading_level:
        readable=True
    if highest_perm_level>=minimum_writing_level:
        writeable=True

    return {"readable":readable, "writeable":writeable}


# Given a user_id and a server_id, this function will return a dict containing bools for all the different permissions in the db based on their role

def get_server_perms(user_id:str, server_id: str) -> ServerPerms:

    # Stuff for testing- ignore

    # user_id='d7c67d16-09b6-4910-9d95-96d3d430a1b9'
    # server_id='ad3f1cd8-ffcd-48ca-abc7-9409c17c9122'

    # Getting the user's roles from MemberInfo with the user_id and the server_id

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

print(get_chat_perms())
print(get_server_perms())