# Contains all server->db functions related to friends and friend requests.
# This includes creating friend request records in the db, updating those entries when
# they are accepted or ignored, etc.
def get_user_friends(user_id: str):
    """
    Retrieves the friends of the given user

    Parameters:
        user_id (str): String containing the "user_id" of the user

    Returns:
        list
    """
    try:
        send_query = """select * from "Discord"."FriendInfo" where sender_id = %s and accepted = %s""" #grabs all friendsinfo data where the user is a sender
        cur.execute(send_query, (user_id, 1))
        records = cur.fetchall()
        friends = [x[2] for x in records] #grabs the user_id for the receiver
        send_query = """select * from "Discord"."FriendInfo" where receiver_id = %s and accepted = %s""" #grabs all friendsinfo data where the user is a receiver
        cur.execute(send_query, (user_id, 1))
        records = cur.fetchall()
        friends.extend([x[2] for x in records]) #grabs the user_id for the sender
        return friends
    except:
        return []

def get_incoming_friend_requests(user_id: str):
    """
    Retrieves the incoming friend requests of the given user

    Parameters:
        user_id (str): String containing the "user_id" of the user

    Returns:
        list
    """
    try:
        send_query = """select * from "Discord"."FriendInfo" where receiver_id = %s and accepted = %s""" #grabs all friendsinfo data where the receiver is the user and they havent accepted the request
        cur.execute(send_query, (user_id, 0))
        records = cur.fetchall()
        friend_requests = [x[0] for x in records] #grabs the friend id for all requests
        return friend_requests
    except:
        return []

def get_unaccepted_sent_friend_requests(user_id: str):
    """
    Retrieves the sent friend requests that are still pending of the given user

    Parameters:
        user_id (str): String containing the "user_id" of the user

    Returns:
        list
    """
    try:
        send_query = """select * from "Discord"."FriendInfo" where sender_id = %s and accepted = %s""" #grabs all friendsinfo data where the sender is the user and the receiver hasn't accepted the request
        cur.execute(send_query, (user_id, 0))
        records = cur.fetchall()
        sent_requests = [x[0] for x in records]
        return sent_requests
    except:
        return []

def accept_friend_request(friend_id: str):
    """
    accepts friend request from the given friend_id

    Parameters:
        friend_id (str): String containing the "user_id" of the friend

    Returns:
        bool
    """
    try:
        send_query = """update "Discord"."FriendInfo" set accepted = %s where friend_id = %s""" #grabs the friendrequest based on the friendid
        cur.execute(send_query, (1, friend_id))
        return True
    except:
        return False

def create_friend_request(user_id: str, friend_user_id: str):
    """
    creates friend request for the given friend_id, from the given user_id

    Parameters:
        user_id (str): String containing the "user_id" of the user
        friend_id (str): String containing the "user_id" of the friend

    Returns:
        bool
    """
    try:
        send_query = """insert into "Discord"."FriendInfo" (friend_id, sender_id, receiver_id, accepted, friend_timestamp) values (%s, %s, %s, %s, %s, %s, %s)"""
        friend_timestamp = str(datetime.datetime.now()) #timestamp
        friend_id = str(uuid4()) #unique friend id
        cur.execute(send_query, (friend_id, user_id, friend_user_id, user_id, friend_user_id, 0, friend_timestamp))
        return True
    except:
        return False