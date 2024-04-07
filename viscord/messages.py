import blessed 

# Creates Terminal Object 
message_term = blessed.Terminal()

print(message_term.clear)
mode = 0

class MessageUI:
    # Terminal Height and Width 
    y = message_term.height 
    x = message_term.width  
    
    # Draw Box Function 
    @staticmethod
    def box_creator(box_height, box_width, box_x_pos, box_y_pos, title, mode=0):
        # Top Border 
        print(message_term.move_yx(box_y_pos, box_x_pos) + message_term.blue(message_term.bold("┌")) + 
            message_term.blue(message_term.bold("─")) * (box_width - 2) + message_term.blue(message_term.bold("┐")))
        # Left and Right Border 
        for i in range (1, box_height-1):
            print(message_term.move_yx(box_y_pos + i, box_x_pos) + message_term.blue(message_term.bold("│")) + message_term.on_gray21(" " * (box_width - 2)) + 
                message_term.blue(message_term.bold('│'))) 
        # Box Title 
        print(message_term.move_yx(box_y_pos - 18, box_x_pos + 32) + title)
        
        # Bottom Border 
        print(message_term.move_yx(box_y_pos + box_height - 1, box_x_pos) + message_term.blue(message_term.bold("└")) + message_term.blue(message_term.bold("─")) * 
              (box_width - 2) + message_term.blue(message_term.bold('┘'))) 
        
        # Check mode for input box
        if mode == 0:
            input_text = ""
            input_box_width = box_width - 4
            input_box_x_pos = box_x_pos + 2
            input_box_y_pos = box_y_pos + box_height - 2
            
            # Draw input box
            print(message_term.move_yx(input_box_y_pos, input_box_x_pos) + message_term.blue(message_term.bold("└")) + 
                  message_term.blue(message_term.bold("─")) * (input_box_width - 1) + message_term.blue(message_term.bold("┘")))
            
            # Start capturing input
            with message_term.cbreak():
                while True:
                    # Move cursor to input box
                    print(message_term.move_yx(input_box_y_pos, input_box_x_pos + 1), end='')
                    # Get user input
                    key = message_term.inkey()
                    if key.is_sequence:
                        if key.name == "KEY_ENTER":
                            break
                        elif key.name == "KEY_BACKSPACE":
                            input_text = input_text[:-1]
                        # Other key handling if needed
                    else:
                        input_text += key

                    # Clear input box and redraw input
                    print(" " * (input_box_width - 1), end='')
                    print(message_term.bold(input_text), end='')

class Message_UI_Movement: 
    print(message_term.clear())
    MessageUI.box_creator(25, 75, 30, 20, message_term.green_on_gray21(message_term.bold("Viscord Chat")), mode)
    
    @staticmethod
    def main(term):
        while True: 
            with term.cbreak(): 
                pinned_open_key_bind = 'p'
                main_open_key_bind = 'm'
                replies_open_key_bind = 'r'
                if term.inkey() == pinned_open_key_bind:
                    print(term.clear())
                    MessageUI.box_creator(25, 75, 30, 20, term.purple_on_gray21(term.bold("Pinned Messages")), mode=1)
                    mode = 1
                if term.inkey() == main_open_key_bind:
                    print(term.clear())
                    MessageUI.box_creator(25, 75, 30, 20, term.green_on_gray21(term.bold("Viscord Chat")), mode=0) 
                    mode = 0  
                if term.inkey() == replies_open_key_bind:
                    print(term.clear()) 
                    MessageUI.box_creator(25, 75, 30, 20, term.red_on_gray21(term.bold("Replies")), mode=3)

class RunUI:
    Message_UI_Movement.main(term)



import psycopg2
import datetime
import random
from uuid import uuid4
from typing import List
from viscord._types import MessageInfo

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"
current_position = 0
def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    return cur

cur = connect_to_db()

def handle_create_message(message_data: dict):
    message_id = str(uuid4())
    user_id = message_data["user_id"]
    server_id = message_data["server_id"]
    chat_id = message_data["chat_id"]
    replied_to_id = message_data.get("replied_to_id")
    message_content = message_data["message_content"]
    message_timestamp = str(datetime.datetime.now())
    pinged_user_ids = message_data.get("pinged_user_ids", [])

    send_query = '''
    INSERT INTO "Discord"."MessageInfo" (message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cur.execute(send_query, (message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids))

def get_recent_messages(data) -> List[MessageInfo]:
    server_id = data["server"]
    chat_id = data["chat"]

    send_query = """
    SELECT message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids
    FROM "Discord"."MessageInfo"
    WHERE server_id = %s AND chat_id = %s
    ORDER BY message_timestamp DESC
    LIMIT 15
    """
    cur.execute(send_query, (server_id,chat_id))
    messages = cur.fetchall()
    messages_data = [
        {
            "message_id": msg[0], 
            "user_id": msg[1], 
            "chat_id": msg[2], 
            "server_id": msg[3],
            "replied_to_id": msg[4], 
            "message_content": msg[5], 
            "message_timestamp": msg[6],
            "pinged_user_ids": msg[7]
        } for msg in messages
    ]
    
    return messages_data

def handle_scroll_messages(scroll_data) -> dict:
    server_id = scroll_data["server"]
    chat_id = scroll_data["chat"]
    start_pos = scroll_data["start_pos"]
    num_requested = scroll_data["num_requested"]

    send_query = """
    SELECT message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp, pinged_user_ids
    FROM "Discord"."MessageInfo"
    WHERE server_id = %s AND chat_id = %s
    ORDER BY message_timestamp DESC
    OFFSET %s
    LIMIT %s
    """
    cur.execute(send_query, (server_id, chat_id, start_pos, num_requested))
    messages = cur.fetchall()
    messages_data = [{"message_id": msg[0], "user_id": msg[1], "chat_id": msg[2], "server_id": msg[3],
                      "replied_to_id": msg[4], "message_content": msg[5], "message_timestamp": msg[6].isoformat(),
                      "pinged_user_ids": msg[7]} for msg in messages]
    return messages_data

def pin_message_in_chat(chat_id, message_id):
    try:
        # Update the ChatInfo table with the new pinned message ID
        update_query = '''
        UPDATE "Discord"."ChatInfo" 
        SET pinned_message_ids = array_append(pinned_message_ids, %s) 
        WHERE chat_id = %s
        '''
        cur.execute(update_query, (message_id, chat_id))
        print("Message pinned ")
    except Exception as e:
        print("pain", e)


message_data =    {
        "user_id": "52f410df-3340-4b32-8b95-46ab5475c2be",
        "chat_id": "7885de7e-eb83-4134-ae29-0df1320177bc",
        "server_id": "acb76574-7a5c-4b5d-ab28-a8ce25982aed",
        "message_content": "Funky Banana Eating Monkeys",
        "pinged_user_ids": ["user1_id", "user2_id"]
    }

handle_create_message(message_data)
print(get_recent_messages({"server":"acb76574-7a5c-4b5d-ab28-a8ce25982aed","chat":"7885de7e-eb83-4134-ae29-0df1320177bc"}))
print("------------------------------------------------------------------------")
