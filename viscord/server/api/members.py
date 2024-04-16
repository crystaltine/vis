from .db import cur
import datetime

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