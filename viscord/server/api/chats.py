from db import cur

def reorder_chats(server_id, chat_name):
    server_id = server_id
    send_query = """select * from "Discord"."ChatInfo" where server_id = %s""" #grabs all chat data for the server_id
    cur.execute(send_query, (server_id,))
    records = cur.fetchall()
    cur_chat = records[0][3]
    if len(records) > 0:
        for x in range(len(records)):
            change_chat = cur_chat
            send_query = """update "Discord"."ChatInfo" set chat_order = %s where chat_name = %s""" #updates the chat_order
            if records[x][3] == chat_name: #if the chat it is updating is the same as the most recently used chat
                cur.execute(send_query, (0, change_chat)) #sets chat_order for chat to 0 and breaks
                break
            cur_chat = records[x + 1][3]
            cur.execute(send_query, ((x + 1), change_chat)) #else moves position of chat up by 1

def handle_reorder_chats(data, conn):
    server_id = data["data"]["server_id"]
    chat_name = data["data"]["chat_name"]
    try:
        reorder_chats(server_id, chat_name)
        conn.sendall("True".encode("utf-8"))
    except Exception as e:
        conn.sendall("False".encode("utf-8"))