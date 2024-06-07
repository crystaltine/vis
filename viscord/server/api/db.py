
import psycopg2

conn_uri = "postgres://avnadmin:AVNS_DyzcoS4HYJRuXlJCxuw@postgresql-terminal-suite-discord-terminal-suite-discord.a.aivencloud.com:15025/Discord?sslmode=require"


def connect_to_db():
    conn = psycopg2.connect(conn_uri)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    return cur

cur = connect_to_db()

