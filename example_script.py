from interpreter import read_styles, read_vis
from globalvars import Globals
from time import sleep
import socket
from typing import TYPE_CHECKING
from text import Text
from logger import Logger
import json
import uuid
from logo import plaster_logo

if TYPE_CHECKING:
    from input import Input
    from div import Div
    from button import Button

# setup socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 5000))

read_styles("example_style.tss")
read_vis("example_doc.vis")

document = Globals.__vis_document__
document.mount()

plaster_logo("50%", "20%")

container: "Div" = document.get_element_by_id("text_container")

username_input: "Input" = document.get_element_by_id("username-input")
password_input: "Input" = document.get_element_by_id("password-input")
submit_button: "Button" = document.get_element_by_id("submit-button")

def submit_handler():
    Logger.log(f"[SUBMIT HANDLER] submitting: {username_input.curr_text=}, {password_input.curr_text=}")
    s.send(json.dumps({
        "type": "login", 
        "data": {
            "user": username_input.curr_text, 
            "password": password_input.curr_text,
            "sys_uuid": uuid.getnode()
        }
    }).encode())
    
    response = s.recv(1024)
    Logger.log(f"[RECEIVED DATA BACK FROM SERVER!!!!!!!!!!!!]: {response=}")

    container.add_child(Text(text=f"your sessionID (very secure i know): {response}", class_str="text1"))
    container.render()

submit_button.on_pressed = submit_handler

while True:
    sleep(1)