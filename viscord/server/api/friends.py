from .db import cur
from typing import List
from ._types import FriendRequestInfo
from uuid import uuid4
import datetime
from .flask_app import app
from .helpers import *
from flask import request

@app.route("/api/friends/outgoing", methods=["POST"])
def get_outgoing_friend_requests() -> List[FriendRequestInfo]:
    """
    Returns a list of outgoing friend requests for to the `user_id` (only the ones they SENT)
    
    if `pending_only` is True, returns only the ones that havent been accepted/ignored. Otherwise returns all requests ever.
    """

    if not validate_fields(request.json, {"user_id": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    if "pending_only" in request.json and isinstance(request.json["pending_only"], bool):
        pending_only = request.json["pending_only"]
    else:
        pending_only = True

    try:
        filter = (0, 0) if pending_only else (1, 0) # if pending_only, only return those where accepted is false

        send_query = """select * from "Discord"."FriendInfo" where sender_id = %s and (accepted = %s or accepted = %s)""" #grabs all friendsinfo data where the user is a sender
        cur.execute(send_query, (user_id, *filter))
        records = cur.fetchall()
        
        data = [
            {
                "friend_id": item[0],
                "sender_id": item[1],
                "receiver_id": item[2],
                "accepted": item[3],
                "friend_timestamp": item[4],
            }
            for item in records
        ]
        return Response(json.dumps({"type": "success", "data": data}), status=200)
    except Exception as e:
        return return_error(e)

@app.route("/api/friends/incoming", methods=["POST"])
def get_incoming_friend_requests() -> List[FriendRequestInfo]:
    """
    Returns a list of incoming friend requests for to the `user_id` (only the ones they are RECEIVING)
    
    if `pending_only` is True, returns only the ones that havent been accepted/ignored. Otherwise returns all requests ever.
    """

    if not validate_fields(request.json, {"user_id": str}):
        return invalid_fields()
    
    user_id = request.json["user_id"]
    if "pending_only" in request.json and isinstance(request.json["pending_only"], bool):
        pending_only = request.json["pending_only"]
    else:
        pending_only = True

    try:

        filter = (0, 0) if pending_only else (1, 0) # if pending_only, only return those where accepted is false

        send_query = """select * from "Discord"."FriendInfo" where receiver_id = %s and (accepted = %s or accepted = %s)""" #grabs all friendsinfo data where the user is a sender
        cur.execute(send_query, (user_id, *filter))
        records = cur.fetchall()
        
        data = [
            {
                "friend_id": item[0],
                "sender_id": item[1],
                "receiver_id": item[2],
                "accepted": item[3],
                "friend_timestamp": item[4],
            }
            for item in records
        ]
        return Response(json.dumps({"type": "success", "data": data}), status=200)
    except Exception as e:
        return return_error(e)

@app.route("/api/friends/accept", methods=["POST"])
def accept_friend_request():
    """
    Accepts a friend request based on the id. Does nothing if already accepted.

    Returns True if successful, false if not
    """

    if not validate_fields(request.json, {"friend_id": str}):
        return invalid_fields()
    
    friend_id = request.json["friend_id"]

    try:
        send_query = """update "Discord"."FriendInfo" set accepted = %s where friend_id = %s""" #grabs the friendrequest based on the friendid
        cur.execute(send_query, (1, friend_id))
        return return_success()
    except Exception as e:
        return return_error(e)
    
@app.route("/api/friends/create", methods=["POST"])
def create_friend_request():
    """
    Creates an unaccepted friend request from the user ids of a sender and receiver.

    Returns True if successful, false if not
    """

    if not validate_fields(request.json, {"sender_id": str, "receiver_id": str}):
        return invalid_fields()
    
    sender_id = request.json["sender_id"]
    receiver_id = request.json["receiver_id"]

    try:
        send_query = """insert into "Discord"."FriendInfo" (friend_id, sender_id, receiver_id, accepted, friend_timestamp) values (%s, %s, %s, %s, %s, %s, %s)"""
        friend_id = str(uuid4()) # create unique friend id
        cur.execute(send_query, (friend_id, sender_id, receiver_id, 0, datetime.datetime.now()))
        return return_success()
    except Exception as e:
        return return_error(e)
    