import psycopg2
from uuid import uuid4
import random
import datetime

# This file will repopulate all tables in the database with some sample data, if the database has to ever be wiped


# Connects to database

conn_uri="postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"

def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    return cur

cur = connect_to_db()

# Hardcoding this information so I can use it across functions

uuid1='b98757df-71aa-4615-8345-26c71cfbb304'
uuid2='d7c67d16-09b6-4910-9d95-96d3d430a1b9'
uuid3='c8fca2c3-0ae9-48d5-8ca5-39e367430f16'

server_id1='ad3f1cd8-ffcd-48ca-abc7-9409c17c9122'
server_id2='d3d2b001-d6a3-4e77-b031-b2f077a13d15'

chat_id1='43eef70b-90bb-40c5-8ece-45abf6a55abb'
chat_id2='741095d5-52e2-424d-b9f5-b3f99ade6b83'
chat_id3='2fe3500c-a2c4-4485-8967-7ab6d649d28f'

message_id1='d40600c5-a7df-4c4a-8250-f46f4fa39c61'

member_role1='da4f865b-cba9-4c6d-bf11-a2ea4ba82ed2'
member_role2='c7667590-5845-453b-a725-1ef6e50f1f4f'
admin_role1='6b42104c-8490-43ea-99d6-da441f07c919'


# This wipes all the content from all the tables (but leaves the tables themselves the same)

def wipe_all_contents() -> None:
    query='''TRUNCATE "Discord"."UserInfo", "Discord"."FriendsInfo", "Discord"."MemberInfo","Discord"."MessageInfo","Discord"."RolesInfo","Discord"."ServerInfo","Discord"."UserInfo" CASCADE;'''
    cur.execute(query)


# This populates the UserInfo table

def populate_user_info() -> None:
    
    # Creating user 1
    
    symbol1 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    color1 = "#ffffff"
    timestamp = str(datetime.datetime.now())
    username1 = 'test_user_1'
    password1 = 'randomsecretpassword45'
    send_query='''insert into "Discord"."UserInfo" (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) values (%s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (uuid1, username1, password1, color1, symbol1, timestamp))

    # Creating user 2
    
    symbol2 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    color2 = "#ffffff"
    timestamp = str(datetime.datetime.now())
    username2 = 'test_user_2'
    password2 = 'randomsecretpassword12'
    send_query='''insert into "Discord"."UserInfo" (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) values (%s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (uuid2, username2, password2, color2, symbol2, timestamp))

    # Creating user 3
    
    symbol3 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    color3 = "#ffffff"
    timestamp = str(datetime.datetime.now())
    username3 = 'test_user_3'
    password3 = 'randomsecretpassword90'
    send_query='''insert into "Discord"."UserInfo" (user_id, user_name, user_password, user_color, user_symbol, user_creation_timestamp) values (%s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (uuid3, username3, password3, color3, symbol3, timestamp))


# This populates the Friends_Info table

def populate_friends_info() -> None:

    # Adding in first friend set between users 1 and 2

    friend_id1 = str(uuid4())
    timestamp = str(datetime.datetime.now())
    send_query='''insert into "Discord"."FriendsInfo" (friend_id, sender_id, receiver_id, accepted, friend_timestamp) values (%s, %s, %s, %s, %s)'''
    
    # I'm going to assume 0 corresponds to not accepted and 1 corresponds to accepted
    
    cur.execute(send_query, (friend_id1, uuid1, uuid2, 0, timestamp))

    # Adding in first friend set between users 1 and 3

    friend_id2 = str(uuid4())
    timestamp = str(datetime.datetime.now())
    send_query='''insert into "Discord"."FriendsInfo" (friend_id, sender_id, receiver_id, accepted, friend_timestamp) values (%s, %s, %s, %s, %s)'''
    cur.execute(send_query, (friend_id2, uuid1, uuid3, 1, timestamp))


# This populates the ServerInfo table

def populate_server_info() -> None:

    # Adding in first server

    server_name1='Test Server 1'
    color1 = "#ffffff"
    server_icon1 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    timestamp = str(datetime.datetime.now())
    send_query='''insert into "Discord"."ServerInfo" (server_id, server__name, color, server_icon, server_creation_timestamp) values (%s, %s, %s, %s, %s)'''
    cur.execute(send_query, (server_id1, server_name1, color1, server_icon1, timestamp))

    # Adding in second server

    server_name2='Test Server 2'
    color2 = "#ffffff"
    server_icon2 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    timestamp = str(datetime.datetime.now())
    send_query='''insert into "Discord"."ServerInfo" (server_id, server__name, color, server_icon, server_creation_timestamp) values (%s, %s, %s, %s, %s)'''
    cur.execute(send_query, (server_id2, server_name2, color2, server_icon2, timestamp))


# This populates the ChatInfo table

def populate_chat_info() -> None:

    # Adding in first chat to first server

    chat_name1='Test Chat 1'
    chat_type1='text'
    chat_topic1='blahblahblah'
    chat_order1=1
    read_perm_level1=1
    write_perm_level1=2
    is_dm1=True
    send_query='''insert into "Discord"."ChatInfo" (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (chat_id1, server_id1, chat_name1, chat_type1, chat_topic1, chat_order1, read_perm_level1, write_perm_level1, is_dm1))

    # Adding in second chat to first server

    chat_name2='Test Chat 2'
    chat_type2='text'
    chat_topic2='blahblahblah2'
    chat_order2=2
    read_perm_level2=2
    write_perm_level2=2
    is_dm2=False
    send_query='''insert into "Discord"."ChatInfo" (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (chat_id2, server_id1, chat_name2, chat_type2, chat_topic2, chat_order2, read_perm_level2, write_perm_level2, is_dm2))

    # Adding in first chat to second server

    chat_name3='Test Chat 1 In a Different Server'
    chat_type3='text'
    chat_topic3='{insert random topic here}'
    chat_order3=1
    read_perm_level3=1
    write_perm_level3=1
    is_dm3=False
    send_query='''insert into "Discord"."ChatInfo" (chat_id, server_id, chat_name, chat_type, chat_topic, chat_order, read_perm_level, write_perm_level, is_dm) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (chat_id3, server_id2, chat_name3, chat_type3, chat_topic3, chat_order3, read_perm_level3, write_perm_level3, is_dm3))


# This populates the MessageInfo table

def populate_message_info() -> None:

    # Adding in first message to first chat in first server

    message_content1='{insert random message content here 1}'
    timestamp = str(datetime.datetime.now())
    send_query='''insert into "Discord"."MessageInfo" (message_id, user_id, chat_id, server_id, message_content, message_timestamp) values (%s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (message_id1, uuid1, chat_id1, server_id1, message_content1, timestamp))

    # Adding in second message to first chat in first server

    message_id2=str(uuid4())
    message_content2='{insert random message reply here 2}'
    timestamp = str(datetime.datetime.now())
    send_query='''insert into "Discord"."MessageInfo" (message_id, user_id, chat_id, server_id, replied_to_id, message_content, message_timestamp) values (%s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (message_id2, uuid2, chat_id1, server_id1, message_id1, message_content2, timestamp))

    # Adding in first message to first chat in second server

    message_id3=str(uuid4())
    message_content3='{insert random message here 3}'
    timestamp = str(datetime.datetime.now())
    send_query='''insert into "Discord"."MessageInfo" (message_id, user_id, chat_id, server_id, message_content, message_timestamp, pinged_user_ids) values (%s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (message_id3, uuid1, chat_id3, server_id2, message_content3, timestamp, [uuid2, uuid3]))


# This populates the Roles_Info table
    
def populate_roles_info() -> None:

    # Adding first member role to first server

    member_role_name1='Member'
    member_role_color1='#ffffff'
    member_role_symbol1=random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    member_priority1=2
    member_permissions1=1
    member_manage_server1=False
    member_manage_chats1=False
    member_manage_chats1=False
    member_manage_members1=False
    member_manage_roles1=False
    member_manage_voice1=False
    member_manage_messages1=False
    member_is_admin1=False
    
    send_query='''insert into "Discord"."RolesInfo" (role_id, server_id, role_name, role_color, role_symbol, priority, permissions, manage_server, manage_chats, \
       manage_members, manage_roles, manage_voice, manage_messages, is_admin) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (member_role1, server_id1, member_role_name1, member_role_color1, member_role_symbol1, member_priority1, member_permissions1, \
        member_manage_server1, member_manage_chats1, member_manage_members1, member_manage_roles1, member_manage_voice1, member_manage_messages1, member_is_admin1))
    
    # Adding first admin role to first server

    admin_role_name1='Admin'
    admin_role_color1='#ffffff'
    admin_role_symbol1=random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    admin_priority1=1
    admin_permissions1=2
    admin_manage_server1=True
    admin_manage_chats1=True
    admin_manage_chats1=True
    admin_manage_members1=True
    admin_manage_roles1=True
    admin_manage_voice1=True
    admin_manage_messages1=True
    admin_is_admin1=True
    send_query='''insert into "Discord"."RolesInfo" (role_id, server_id, role_name, role_color, role_symbol, priority, permissions, manage_server, manage_chats, \
       manage_members, manage_roles, manage_voice, manage_messages, is_admin) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (admin_role1, server_id1, admin_role_name1, admin_role_color1, admin_role_symbol1, admin_priority1, admin_permissions1, admin_manage_server1, \
        admin_manage_chats1, admin_manage_members1, admin_manage_roles1, admin_manage_voice1, admin_manage_messages1, admin_is_admin1))

    # Adding first member role to second server

    member_role_name2='Member'
    member_role_color2='#ffffff'
    member_role_symbol2=random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    member_priority2=2
    member_permissions2=1
    member_manage_server2=False
    member_manage_chats2=False
    member_manage_chats2=False
    member_manage_members2=False
    member_manage_roles2=False
    member_manage_voice2=False
    member_manage_messages2=False
    member_is_admin2=False
    send_query='''insert into "Discord"."RolesInfo" (role_id, server_id, role_name, role_color, role_symbol, priority, permissions, manage_server, manage_chats, \
       manage_members, manage_roles, manage_voice, manage_messages, is_admin) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (member_role2, server_id2, member_role_name2, member_role_color2, member_role_symbol2, member_priority2, member_permissions2, \
        member_manage_server2, member_manage_chats2, member_manage_members2, member_manage_roles2, member_manage_voice2, member_manage_messages2, member_is_admin2))


# This populates the MemberInfo table
    
def populate_member_info() -> None:

    # Adding in user1 as a member in the first server

    member_id1=str(uuid4())
    nickname1='{shortened version of name 1}'
    nick_symbol1 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    nick_color1 = "#ffffff"
    timestamp = str(datetime.datetime.now())
    roles_list1=[member_role1]
    send_query='''insert into "Discord"."MemberInfo" (member_id, user_id, server_id, nickname, nick_symbol, nick_color, member_join_date, roles_list) values (%s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (member_id1, uuid1, server_id1,nickname1, nick_symbol1, nick_color1, timestamp, roles_list1))

    # Adding in user2 as an admin in the first server

    member_id2=str(uuid4())
    nickname2='{shortened version of name 2}'
    nick_symbol2 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    nick_color2 = "#ffffff"
    timestamp = str(datetime.datetime.now())
    roles_list2=[admin_role1]
    send_query='''insert into "Discord"."MemberInfo" (member_id, user_id, server_id, nickname, nick_symbol, nick_color, member_join_date, roles_list) values (%s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (member_id2, uuid2, server_id1,nickname2, nick_symbol2, nick_color2, timestamp, roles_list2))

    # Adding in user1 as a member in the second server

    member_id3=str(uuid4())
    nickname3='{shortened version of name 3}'
    nick_symbol3 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    nick_color3 = "#ffffff"
    timestamp = str(datetime.datetime.now())
    roles_list3=[member_role2]
    send_query='''insert into "Discord"."MemberInfo" (member_id, user_id, server_id, nickname, nick_symbol, nick_color, member_join_date, roles_list) values (%s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (member_id3, uuid1, server_id2, nickname3, nick_symbol3, nick_color3, timestamp, roles_list3))

    # Adding in user2 as a member in the second server

    member_id4=str(uuid4())
    nickname4='{shortened version of name 4}'
    nick_symbol4 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    nick_color4 = "#ffffff"
    timestamp = str(datetime.datetime.now())
    roles_list4=[member_role2]
    send_query='''insert into "Discord"."MemberInfo" (member_id, user_id, server_id, nickname, nick_symbol, nick_color, member_join_date, roles_list) values (%s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (member_id4, uuid2, server_id2, nickname4, nick_symbol4, nick_color4, timestamp, roles_list4))

    # Adding in user3 as a member in the second server

    member_id5=str(uuid4())
    nickname5='{shortened version of name 4}'
    nick_symbol5 = random.choice("☀☁★☾♥♠♦♣♫☘☉☠")
    nick_color5 = "#ffffff"
    timestamp = str(datetime.datetime.now())
    roles_list5=[member_role2]
    send_query='''insert into "Discord"."MemberInfo" (member_id, user_id, server_id, nickname, nick_symbol, nick_color, member_join_date, roles_list) values (%s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.execute(send_query, (member_id5, uuid3, server_id2, nickname5, nick_symbol5, nick_color5, timestamp, roles_list5))


wipe_all_contents()
populate_user_info()
populate_friends_info()
populate_server_info()
populate_chat_info()
populate_message_info()
populate_roles_info()
populate_member_info()