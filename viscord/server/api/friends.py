from .db import cur
from typing import List
from ._types import FriendRequestInfo
from uuid import uuid4
import datetime

def get_outgoing_friend_requests(user_id: str, pending_only: bool = True) -> List[FriendRequestInfo]:
    """
    Returns a list of outgoing friend requests for to the `user_id` (only the ones they SENT)
    
    if `pending_only` is True, returns only the ones that havent been accepted/ignored. Otherwise returns all requests ever.
    """

    filter = (0, 0) if pending_only else (1, 0) # if pending_only, only return those where accepted is false

    send_query = """select * from "Discord"."FriendInfo" where sender_id = %s and (accepted = %s or accepted = %s)""" #grabs all friendsinfo data where the user is a sender
    cur.execute(send_query, (user_id, *filter))
    records = cur.fetchall()
    
    return [
        {
            "friend_id": item[0],
            "sender_id": item[1],
            "receiver_id": item[2],
            "accepted": item[3],
            "friend_timestamp": item[4],
        }
        for item in records
    ]

def outgoing_friends_endpoint(data, conn):
    user_id = data["data"]["user_id"]
    if "pending_only" in data["data"]:
        pending_only = data["data"]["pending_only"]
    else:
        pending_only = True
    try:
        friends = get_outgoing_friend_requests(user_id, pending_only=pending_only)
        conn.sendall(str(friends).encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))

def get_incoming_friend_requests(user_id: str, pending_only: bool = True) -> List[FriendRequestInfo]:
    """
    Returns a list of incoming friend requests for to the `user_id` (only the ones they are RECEIVING)
    
    if `pending_only` is True, returns only the ones that havent been accepted/ignored. Otherwise returns all requests ever.
    """

    filter = (0, 0) if pending_only else (1, 0) # if pending_only, only return those where accepted is false

    send_query = """select * from "Discord"."FriendInfo" where receiver_id = %s and (accepted = %s or accepted = %s)""" #grabs all friendsinfo data where the user is a sender
    cur.execute(send_query, (user_id, *filter))
    records = cur.fetchall()
    
    return [
        {
            "friend_id": item[0],
            "sender_id": item[1],
            "receiver_id": item[2],
            "accepted": item[3],
            "friend_timestamp": item[4],
        }
        for item in records
    ]


def incoming_friends_endpoint(data, conn):
    user_id = data["data"]["user_id"]
    if "pending_only" in data["data"]:
        pending_only = data["data"]["pending_only"]
    else:
        pending_only = True
    try:
        friends = get_incoming_friend_requests(user_id, pending_only=pending_only)
        conn.sendall(str(friends).encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))

def accept_friend_request(friend_id: str):
    """
    Accepts a friend request based on the id. Does nothing if already accepted.

    Returns True if successful, false if not
    """
    try:
        send_query = """update "Discord"."FriendInfo" set accepted = %s where friend_id = %s""" #grabs the friendrequest based on the friendid
        cur.execute(send_query, (1, friend_id))
        return True
    except:
        return False
    
def accept_friend_request_endpoint(data, conn):
    friend_id = data["data"]["friend_id"]
    try:
        if accept_friend_request(friend_id):
            conn.sendall("True".encode("utf-8"))
        else:
            conn.sendall("False".encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))

def create_friend_request(sender_id: str, receiver_id: str) -> bool:
    """
    Creates an unaccepted friend request from the user ids of a sender and receiver.

    Returns True if successful, false if not
    """
    try:
        send_query = """insert into "Discord"."FriendInfo" (friend_id, sender_id, receiver_id, accepted, friend_timestamp) values (%s, %s, %s, %s, %s, %s, %s)"""
        friend_id = str(uuid4()) # create unique friend id
        cur.execute(send_query, (friend_id, sender_id, receiver_id, 0, datetime.datetime.now()))
        return True
    except:
        return False
    
def create_friend_request_endpoint(data, conn):
    sender_id = data["data"]["sender_id"]
    receiver_id = data["data"]["receiver_id"]
    try:
        if create_friend_request(sender_id, receiver_id):
            conn.sendall("True".encode("utf-8"))
        else:
            conn.sendall("False".encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))