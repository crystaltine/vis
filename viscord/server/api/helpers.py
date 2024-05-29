import json
from flask import Response
from .login_flow import tokens
import requests
from .server_config import URI 

def member_perms(user_token: str, server_id: str, chat_id: str) -> bool:
    try:
        resp = requests.post(URI + "/api/roles/get_chat_perms", json={"chat_id": chat_id, "server_id": server_id})
        if resp.status_code != 200:
            return {"readable": False, "writable": False}
        return resp.json()["data"]
    except Exception as e:
        return {"readable": False, "writable": False}

def validate_fields(data, name_type):
    for name, type_ in name_type.items():
        if name not in data:
            return False
        if not isinstance(data[name], type_):
            return False
    return True

def validate_color(color: str) -> bool:
    if len(color) != 7: # must be #xxxxxx format
        return False
    if not all([c in "1234567890abcdef" for c in color.lower()[1:]]):
        return False
    return True


def invalid_fields():
    return Response(
        json.dumps({"type": "incorrect", "message": "Invalid fields"}),
        status=400)

def return_error(e):
    print("Request error: " + str(e))
    return Response(
        json.dumps({"type": "error", "message": str(e)}),
        status=500)

def return_success():
    return Response(
        json.dumps({"type": "success"}),
        status=200)

def missing_permissions():
    return Response(
        json.dumps({"type": "incorrect", "message": "You do not have permission to perform this action"}),
        status=403)

def is_valid_token(token: str) -> bool:
    return token in tokens

def get_user_id(token: str) -> str:
    name, _id = tokens.get_id(token)
    return _id

def forbidden():
    return Response(
        json.dumps({"type": "incorrect", "message": "Invalid token"}),
        status=403)