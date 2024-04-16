import socket
import threading
import json
import os
import api.users, api.login_flow, api.messages, api.chats

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5000))

print("Server up!")
print("Running on " + str(s.getsockname()[0]) + ":" + str(s.getsockname()[1]))

connections = {}



def handle_message(data, conn):
    send = json.dumps(data).encode()
    print("New message:", data["data"])
    for addr2 in connections:
        if addr2 != data["from"]:
            try:
                connections[addr2].sendall(send)
            except:
                print(f"Error sending to {addr2}, removing...")
                del connections[addr2]


''' 
def handle_recent_messages(data, conn):
    server_id = data["data"]

    send_query = """
    SELECT message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids
    FROM "Discord"."MessageInfo"
    WHERE server_id = %s
    ORDER BY message_timestamp DESC
    LIMIT 15
    """
    cur.execute(send_query, (server_id,))
    messages = cur.fetchall()
    messages_data = [{"message_id": msg[0], "user_id": msg[1], "chat_id": msg[2], "server_id": msg[3],
                      "replied_to_id": msg[4], "message_content": msg[5], "message_timestamp": msg[6].isoformat(),
                      "pinged_user_ids": msg[7]} for msg in messages]
    conn.sendall(json.dumps(messages_data).encode("utf-8"))

def handle_scroll_messages(data, conn):
    scroll_data = data["data"]
    server_id = scroll_data["server_id"]
    current_position = scroll_data.get("current_position", 0)
    direction = scroll_data["direction"]

    if direction == "up":
        current_position -= 1
        if current_position < 0:
            current_position = 0
    else:  # direction == "down"
        current_position += 1

    send_query = """
    SELECT message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids
    FROM "Discord"."MessageInfo"
    WHERE server_id = %s
    ORDER BY message_timestamp DESC
    OFFSET %s
    LIMIT 15
    """
    cur.execute(send_query, (server_id, current_position))
    messages = cur.fetchall()
    messages_data = [{"message_id": msg[0], "user_id": msg[1], "chat_id": msg[2], "server_id": msg[3],
                      "replied_to_id": msg[4], "message_content": msg[5], "message_timestamp": msg[6].isoformat(),
                      "pinged_user_ids": msg[7]} for msg in messages]
    conn.sendall(json.dumps({"messages": messages_data, "current_position": current_position}).encode("utf-8"))
'''
tokens = {}
handlers = {
    "msg": handle_message,
    "account_create": api.users.handle_account_creation,
    "username_check": api.users.handle_username_check,
    "login": api.login_flow.handle_login,
#    "recent_messages": handle_recent_messages,
#    "scroll_messages": handle_scroll_messages
    "token_bypass": api.login_flow.handle_token_bypass,
    "pin_message": api.messages.pin_message_endpoint,
    "handle_user_name_update": api.users.update_username_endpoint,
    "handle_user_password_update": api.users.update_password_endpoint,
    "handle_user_color_update": api.users.update_color_endpoint,
    "handle_user_symbol_update": api.users.update_symbol_endpoint,
    "handle_reorder_chats": api.chats.handle_reorder_chats,
    

}

def handle_connection(conn, addr):
    print("New connection:", addr)
    connections[addr] = conn
    while True:
        try:
            data = conn.recv(1024)
        except:
            pass
        else:
            if not data:
                print("Disconnect:", addr)
                del connections[addr]
                return
            parsed = json.loads(data.decode())
            for label in handlers:
                if "type" in parsed and parsed["type"] == label:
                    parsed["from"] = addr
                    print("Endpoint " + label + " called by " )
                    handlers[label](parsed, conn)
                    break


while True:
    s.listen()
    conn, addr = s.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
