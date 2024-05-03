create schema "Discord";
set search_path to "Discord",public;


create table "Discord"."UserInfo"(
	user_id varchar(512) primary key not null,
	user_name varchar(512) not null,
	user_password varchar(512) not null,
	user_color varchar(512) not null,
	user_symbol varchar(512) not null,
	user_creation_timestamp timestamp not null
);

create table "Discord"."ServerInfo" (
	server_id varchar(512) primary key not null,
	server__name varchar(512) not null,
	server_owner varchar(512) not null,
	constraint server_info_user_id foreign key(server_owner) references "Discord"."UserInfo"(user_id),
	color varchar(512) not null,
	server_icon varchar(512) not null,
	server_creation_timestamp timestamp not null
);

create table "Discord"."ChatInfo" (
	chat_id varchar(512) primary key not null,
	server_id varchar(512) not null,
	constraint chat_info_server_id foreign key(server_id) references "Discord"."ServerInfo"(server_id),
	chat_name varchar(512) not null,
	chat_type varchar(512) not null,
	chat_topic varchar(512) not null,
	chat_order int not null,
	read_perm_level int not null,
	write_perm_level int not null,
	is_dm bool not null,
	pinned_message_ids varchar(512)[]
);

create table "Discord"."MessageInfo"(
	message_id varchar(512) primary key not null,
	user_id varchar(512) not null,
	chat_id varchar(512) not null,
	server_id varchar(512) not null,
	replied_to_id varchar(512),
	constraint message_info_user_id foreign key(user_id) references "UserInfo"(user_id),
	constraint message_info_chat_id foreign key(chat_id) references "ChatInfo"(chat_id),
	constraint message_info_server_id foreign key(server_id) references "ServerInfo"(server_id),
	message_content varchar(512) not null,
	message_timestamp timestamp not null,
	pinged_user_ids varchar(512)[],
	constraint message_info_replied_to_id foreign key(replied_to_id) references "MessageInfo"(message_id)
);

create table "Discord"."RolesInfo" (
	role_id varchar(512) primary key not null,
	server_id varchar(512) not null,
	constraint roles_info_server_id foreign key(server_id) references "ServerInfo"(server_id),
	role_name varchar(512) not null,
	role_color varchar(512) not null,
	role_symbol varchar(512) not null,
	priority int not null,
	permissions int not null,
	manage_server bool not null,
	manage_chats bool not null,
	manage_members bool not null,
	manage_roles bool not null,
	manage_voice bool not null,
	manage_messages bool not null,
	is_admin bool not null
	
);

create table "Discord"."MemberInfo" (
	member_id varchar(512) primary key not null,
	user_id varchar(512) not null,
	server_id varchar(512) not null,
	constraint member_info_user_id foreign key(user_id) references "UserInfo"(user_id),
	constraint member_info_server_id foreign key(server_id) references "ServerInfo"(server_id),
	nickname varchar(512),
	nick_symbol varchar(512),
	nick_color varchar(512),
	member_join_date timestamp not null,
	roles_list varchar(512)[]
);


create table "Discord"."FriendsInfo" (
	friend_id varchar(512) primary key not null,
	sender_id varchar(512) not null,
	receiver_id varchar(512) not null,
	constraint friends_info_sender_id foreign key(sender_id) references "UserInfo"(user_id),
	constraint friends_info_receiver_id foreign key(receiver_id) references "UserInfo"(user_id),
	accepted int not null,
	friend_timestamp timestamp not null
);

create table "Discord"."InvitesInfo" (
	invite_id varchar(512) primary key not null,
	server_id varchar(512) not null,
	constraint invites_info_server_id foreign key(server_id) references "ServerInfo"(server_id),
	invite_code varchar(512) not null,
	invite_creator_id varchar(512) not null,
	constraint invites_info_invite_creator_id foreign key(invite_creator_id) references "UserInfo"(user_id)
);