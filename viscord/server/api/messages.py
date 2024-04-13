from db import cur

def pin_message(message_id, channel_id):
    send_query = '''select pinned_message_ids from "Discord"."ChatInfo" where chat_id = %s'''
    cur.execute(send_query, (channel_id,))
    records = cur.fetchall()
    if len(records) == 0:
        return False
    
    pinned_message_ids = records[0][0]
    if pinned_message_ids == None:
        pinned_message_ids = []

    if message_id in pinned_message_ids:
        return False
    
    pinned_message_ids.append(message_id)
    send_query = '''update "Discord"."ChatInfo" set pinned_message_ids = %s where chat_id = %s'''
    try:
        cur.execute(send_query, (pinned_message_ids, channel_id))
        return True
    except Exception as e:
        return False

def pin_message_endpoint(data, conn):
    data = data["data"]
    message_id = data["message_id"]
    channel_id = data["channel_id"]

    if pin_message(message_id, channel_id):
        if conn:
            conn.sendall("True".encode("utf-8"))
    else:
        if conn:
            conn.sendall("False".encode("utf-8"))
