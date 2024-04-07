def get_server_perms(user_id:str, server_id: str, cur):
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
