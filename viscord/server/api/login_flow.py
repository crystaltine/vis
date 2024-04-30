from .db import cur
from cryptography.fernet import Fernet
import os
from uuid import uuid4

from flask import request, Response
from .flask_app import app
from .helpers import *
import json

key = os.getenv("VISCORD_KEY")
if not key:
    key = Fernet.generate_key()
    os.system("export VISCORD_KEY=" + key.decode())
else:
    key = key.encode()

tokens = {}

@app.route("/api/login", methods=["POST"])
def handle_login():

    if not validate_fields(request.json, {"user": str, "password": str, "sys_uuid": str}): 
        return invalid_fields()

    user = request.json["user"]
    password = request.json["password"]
    sys_uuid = request.json["sys_uuid"]

    send_query = """select user_id, user_name from "Discord"."UserInfo" where user_name = %s and user_password = %s"""
    try:
        cur.execute(send_query, (user, password))
        records = cur.fetchall()
        if len(records) > 0:
            token = str(uuid4())
            tokens[token] = user
            f = Fernet(key + str(sys_uuid).encode())
            cache = f.encrypt(token.encode("utf-8")).decode("utf-8")

            d = {"type": "success", "token": token, "cache": cache, "user_id": records[0][0], "username": records[0][1]}
            return Response(json.dumps(d), status=200)
        else:
            d = {"type": "invalid", "message": "Invalid credentials"}
            return Response(json.dumps(d), status=403)
    except Exception as e:
        return Response(json.dumps({"type": "error", "message": str(e)}), status=500)


@app.route("/api/login/bypass", methods=["POST"])
def handle_token_bypass():
    if not validate_fields(request.json, {"cache": str, "sys_uuid": str}):
        return invalid_fields()
    
    cache = request.json["cache"]
    sys_uuid = request.json["sys_uuid"]


    try:
        f = Fernet(key + str(sys_uuid).encode())
        token = f.decrypt(cache.encode("utf-8")).decode("utf-8")

        name = tokens[token]
        query = """select user_id, user_name from "Discord"."UserInfo" where user_name = %s"""
        cur.execute(query, (name,))
        records = cur.fetchall()
        if len(records) == 0:
            return Response(json.dumps({"type": "invalid", "message": "Invalid token"}), status=403)
        d = {"type": "success", "token": token, "user_id": records[0][0], "username": records[0][1]}
        return Response(json.dumps(d), status=200)
    except Exception as e:
        return Response(json.dumps({"type": "error", "message": str(e)}), status=500)