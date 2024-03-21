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

#creates server given the server data - if data is null will create a test server with preset information
def handle_server_creation(data):
    server_id = str(uuid4())
    print("Server ID: " + server_id)
    server_timestamp = str(datetime.datetime.now())
    server_name = None
    server_icon = None
    server_color = None
    if data is None:
        server_id = server_id
        server_name = "test_server"
        server_icon = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
        server_color = "#ffffff"
    else:
        server_name = data["server_name"]
        server_icon = data["server_symbol"]
        server_color = data["server_color"]

    send_query='''
        INSERT into "Discord"."ServerInfo" (server_id, server__name, color, server_icon, server_creation_timestamp) values (%s, %s, %s, %s, %s)
    '''
    cur.execute(send_query, (server_id, server_name, server_color, server_icon, server_timestamp))

#updates name of a server in the database given the server's id
def handle_server_name_update(server_id, new_server_name):
    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET server__name = %s
        WHERE server_id = %s
    '''    
    cur.execute(send_query, (new_server_name, server_id))

#updates color of a server in the database given the server's id
def handle_server_color_update(server_id, new_color_color):
    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET color = %s
        WHERE server_id = %s
    '''    
    cur.execute(send_query, (new_color_color, server_id))

#updates icon of a server in the database given the server's id
def handle_server_icon_update(server_id, new_server_icon):
    send_query = '''
        UPDATE "Discord"."ServerInfo"
        SET server_icon = %s
        WHERE server_id = %s
    '''    
    cur.execute(send_query, (new_server_icon, server_id))

#test command to retrieve information about a server - so I can test other commands
def test_retrieve_server_information(server_id):
    send_query = '''
        SELECT * FROM "Discord"."ServerInfo"
        WHERE server_id = %s
    '''
    cur.execute(send_query, (server_id,))
    records = cur.fetchall()
    if records:
        print("Server Information:")
        for result in records:
            print("Server ID:", result[0])
            print("Server Name:", result[1])
            print("Server Color:", result[2])
            print("Server Icon:", result[3])
            print("Server Creation Timestamp:", result[4])
            print("--------------------------------")
    else:
        print("Server not found")



handle_server_creation(None)
server_id = input("Enter server id: ")
test_retrieve_server_information(server_id)
print()
print("Updating user name...")
print()
handle_server_name_update(server_id, "NEWNAME")
print()
print("Updating server color...")
print()
handle_server_color_update(server_id, "#000000")
print()
print("Updating server icon...")
print()
handle_server_icon_update(server_id, "☉")
test_retrieve_server_information(server_id)




