from .db import cur
from uuid import uuid4
import datetime

def get_user_friends(user_id):
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

def get_incoming_friend_requests(user_id):
    try:
        send_query = """select * from "Discord"."FriendInfo" where receiver_id = %s and accepted = %s""" #grabs all friendsinfo data where the receiver is the user and they havent accepted the request
        cur.execute(send_query, (user_id, 0))
        records = cur.fetchall()
        friend_requests = [x[0] for x in records] #grabs the friend id for all requests
        return friend_requests
    except:
        return []

def get_unaccepted_sent_friend_requests(user_id):
    try:
        send_query = """select * from "Discord"."FriendInfo" where sender_id = %s and accepted = %s""" #grabs all friendsinfo data where the sender is the user and the receiver hasn't accepted the request
        cur.execute(send_query, (user_id, 0))
        records = cur.fetchall()
        sent_requests = [x[0] for x in records]
        return sent_requests
    except:
        return []

def accept_friend_request(friend_id):
    try:
        send_query = """update "Discord"."FriendInfo" set accepted = %s where friend_id = %s""" #grabs the friendrequest based on the friendid
        cur.execute(send_query, (1, friend_id))
        return True
    except:
        return False

def create_friend_request(user_id, friend_user_id):
    try:
        send_query = """insert into "Discord"."FriendInfo" (friend_id, sender_id, receiver_id, accepted, friend_timestamp) values (%s, %s, %s, %s, %s, %s, %s)"""
        friend_timestamp = str(datetime.datetime.now()) #timestamp
        friend_id = str(uuid4()) #unique friend id
        cur.execute(send_query, (friend_id, user_id, friend_user_id, user_id, friend_user_id, 0, friend_timestamp))
        return True
    except:
        return False