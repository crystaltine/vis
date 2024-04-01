import psycopg2
from Movement_between_messageUIs import Message_UI_Movement
import blessed
conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

Message_UI_Movement.movement(blessed.Terminal())

def reply_to_message(user_id, message_id, message_content, replied_to_id=None):
        cur.execute("""
            INSERT INTO Discord.MessageInfo (message_id, replied_to_id, message_content, )
            VALUES (%s, %s, %s, %s, %s);
        """,(message_id, replied_to_id, message_content)) 


        cur.commit()

        print("Message sent successfully!")

reply_to_message(user_id="sender_user_id", message_id= "0123", message_content="Your reply message content", replied_to_id="id_of_the_message_being_replied_to")

    

    

    


