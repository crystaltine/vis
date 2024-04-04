
import psycopg2

 

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()


def change_user_name(new_user_name):
    send_query='''select user_name FROM "Discord"."UserInfo" '''
    cur.execute(send_query)
    data = cur.fetchall()
    available_name_bool = True
    for user in data:
        if new_user_name == user: 
            print("Taken by Another User") 
            available_name_bool = False
            break 
    if available_name_bool: 
        send_query = '''insert into "Discord"."UserInfo" (user_name = %s)'''
        cur.execute(send_query, (new_user_name))

def change_user_password(new_user_password, user_name):
    send_query='''select user_password FROM "Discord"."UserInfo" '''
    cur.execute(send_query)
    data = cur.fetchall()
    available_password_bool = True
    for password in data:
        if new_user_password == password: 
            print("Taken by Another User") 
            available_password_bool = True
            break 
    if available_password_bool: 
        send_query = '''insert into "Discord"."UserInfo" (user_password) values (%s) where (user_name = %s)'''
        cur.execute(send_query, (new_user_password, user_name))

def change_user_color(color):
        send_query = '''update "Discord"."UserInfo" (user_color = %s) where (user_name = %s)'''
        cur.execute(send_query, (color))

def update_user_symbol(user_name, symbol):
    send_query = """update "Discord"."UserInfo" set user_symbol = %s where user_name = %s"""
    cur.execute(send_query, (symbol, user_name))

    
