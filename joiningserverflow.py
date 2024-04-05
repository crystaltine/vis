from invites import handle_invite_creation, handle_check_existing_invite, handle_join_code_validation
from role_perms import get_server_perms
from uuid import uuid4
from members import handle_member_creation

# ok, so the flow
# gonna be like this
# 1. server admin creates a join server code (6 character long thingy)
# 2. server admin sends this code to the user
# 3. user uses this code to join the server
# 4. tada! user is now a member of the server

# call when server admin wants to invite someone to the server
# will return a 6 digit join code (either a pre-existing one or a new one if no previous invite exists)
def handle_server_invite_request(user_id: str, server_id: str) -> str:
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

    perms = get_server_perms(user_id, server_id)

    if perms['manage_server'] == False:
        print("You do not have permission to create invites for this server.")
        return

    # check if there is an existing invite for this server

    existing_invite = handle_check_existing_invite(server_id)

    # if there is an existing invite, return it

    if existing_invite:
        return existing_invite

    # if there is no existing invite, create a new one and return it

    invite_code = str(uuid4())[:6]
    
    handle_invite_creation(user_id, server_id, invite_code)

    return invite_code

# will check join code user enters and if its valid add them to the server
def handle_user_joining_server(user_id: str, invite_code: str):
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

    server_id =  handle_join_code_validation(invite_code)

    if server_id:
        handle_member_creation(user_id, server_id)
    else:
        print("Invalid invite code. Please try again.")
        return

