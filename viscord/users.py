import psycopg2
import datetime
import random
from uuid import uuid4

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

#test command to create a basic user - so I can test other commands 
def test_user_creation(user_id):
    symbol = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    color = "#ffffff"
    timestamp = str(datetime.datetime.now())
    username = "test"
    password = "verysecretpassword"

    send_query='''
        INSERT into "Discord"."UserInfo" (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) values (%s, %s, %s, %s, %s, %s)
    '''
    cur.execute(send_query, (user_id, username, password, color, symbol, timestamp))

def handle_user_name_update(user_id: str, new_user_name: str) -> None:
    """
    Update the username of a user in the database given the user's id.

    Parameters:
        user_id (str): The id of the user whose username is to be updated.
        new_user_name (str): The new username for the user.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_name = %s
        WHERE user_id = %s
    '''    
    cur.execute(send_query, (new_user_name, user_id))

def handle_user_password_update(user_id: str, new_password: str) -> None:
    """
    Update the password of a user in the database given the user's id.

    Parameters:
        user_id (str): The id of the user whose password is to be updated.
        new_password (str): The new password for the user.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_password = %s
        WHERE user_id = %s
    '''    
    cur.execute(send_query, (new_password, user_id))

def handle_user_color_update(user_id: str, new_user_color: str) -> None:
    """
    Update the color of a user in the database given the user's id.

    Parameters:
        user_id (str): The id of the user whose color is to be updated.
        new_user_color (str): The new color for the user.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_color = %s
        WHERE user_id = %s
    '''    
    cur.execute(send_query, (new_user_color, user_id))

def handle_user_symbol_update(user_id: str, new_user_symbol: str) -> None:
    """
    Update the symbol of a user in the database given the user's id.

    Parameters:
        user_id (str): The id of the user whose symbol is to be updated.
        new_user_symbol (str): The new symbol for the user.

    Returns:
        None
    """
    send_query = '''
        UPDATE "Discord"."UserInfo"
        SET user_symbol = %s
        WHERE user_id = %s
    '''    
    cur.execute(send_query, (new_user_symbol, user_id))

def test_retrieve_user_information(user_id: str) -> None:
    """
    Retrieve information about a user from the database given the user's id.

    Parameters:
        user_id (str): The id of the user to retrieve information for.

    Returns:
        None
    """
    send_query = '''
        SELECT * FROM "Discord"."UserInfo"
        WHERE user_id = %s
    '''
    cur.execute(send_query, (user_id,))
    records = cur.fetchall()
    if records:
        print("User Information:")
        for result in records:
            print("User ID:", result[0])
            print("User Name:", result[1])
            print("User Password:", result[2])
            print("User Color:", result[3])
            print("User Symbol:", result[4])
            print("User Creation Timestamp:", result[5])
            print("--------------------------------")
    else:
        print("User not found")

test_user_id = str(uuid4())
test_user_creation(test_user_id)
test_retrieve_user_information(test_user_id)
print()
print("Updating user name...")
print()
handle_user_name_update(test_user_id, "newusername")
print()
print("Updating user password...")
print()
handle_user_password_update(test_user_id, "☉")
print()
print("Updating user color...")
print()
handle_user_color_update(test_user_id, "#000000")
print()
print("Updating user symbol...")
print()
handle_user_symbol_update(test_user_id, "newusername")
test_retrieve_user_information(test_user_id)




