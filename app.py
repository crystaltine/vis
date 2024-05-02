from interpreter import read_styles, read_vis
from globalvars import Globals
from logger import Logger
from utils import cls
from div import Div
from text import Text
from scrollbox import Scrollbox
from input import Input
from button import Button

import requests
import socket
import uuid

class mem:
    on_messages_screen = False
    sock: socket.socket = None 

    token: str = None
    cache: str = None
    user_id: str = None
    username: str = None

def Message(content: str) -> Div:
    """
    Generic message component
    """
    return Div(
        class_str="message-obj",
        children=[
            Text(
                class_str="message-obj-author",
                text="@a_random_user"
            ),
            Text(
                class_str="message-obj-content",
                text=content
            ),
        ]
    )

def ServerItem(name: str, color: str) -> Text:
    return Text(
        class_str="server-obj",
        style=f"color: {color}",
        text=name,
    )

def ChatItem(name: str, color: str) -> Text:
    return Text(
        class_str="server-obj",
        style=f"color: {color}",
        text=name,
    )

def submit_handler_wrapper():
    try:
        submit_handler()
    except Exception as e:
        Logger.log(f"[submit handler wrapper] exception: {e}")
        error_message.text = "Failed to log in (B)! Try again later."
        error_message.render()

def submit_handler():
    res = requests.post("http://127.0.0.1:5000/api/login", json={
        "user": username_input.curr_text,
        "password": password_input.curr_text,
        "sys_uuid": str(uuid.getnode())
    })

    data = res.json()

    mem.user_id = data['user_id']
    mem.token = data['token']
    mem.cache = data['cache']
    mem.username = data['username']
    
    Logger.log(f"[submit handler] response json['type']: {data.get('type')} <- exception incoming if none")
    if data['type'] == 'success':
        mem.on_messages_screen = True
        init_messages_socket()

    elif data['type'] == 'invalid':
        error_message.text = "Incorrect credentials!"
    else: 
        error_message.text = "Failed to log in (A)! Try again later."
    error_message.render()

def init_messages_socket():
    # set up message socket
        mem.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mem.sock.connect(("127.0.0.1", 5001))
        # immediately send our token
        mem.sock.send(mem.token)

        def socket_listen_loop():
            pass
            # TODO

def send_message(content: str):
    mem.sock.send({
        "token": mem.token,
        "author": mem.username,
        "content": content,
    })

def main():
    
    read_styles("login_style.tss")
    read_vis("login_layout.vis")

    document = Globals.__vis_document__

    container: "Div" = document.get_element_by_id("text_container")

    username_input: "Input" = document.get_element_by_id("username-input")
    password_input: "Input" = document.get_element_by_id("password-input")
    submit_button: "Button" = document.get_element_by_id("submit-button")
    error_message: "Text" = document.get_element_by_id("error_message")

    submit_button.on_pressed = submit_handler_wrapper
    document.mount()

    while True:
        if mem.on_messages_screen:

            # setup socket
            try:
                submit_handler()
            except Exception as e:
                error_message.text = "Couldn't connect to server!"
                error_message.render()

        def submit_handler():
            
            res = requests.post("http://127.0.0.1:5000/api/login", json={
                "user": username_input.curr_text,
                "password": password_input.curr_text,
                "sys_uuid": str(uuid.getnode())
            })

            data = res.json()
            
            if data['type'] == 'success':
                test.on_messages_screen = True  

        submit_button.on_pressed = submit_handler_wrapper
        document.mount()

        while True:
            if test.on_messages_screen:

                # setup socket
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(("localhost", 5000))
                except Exception as e:
                    cls()
                    print(f"\x1b[31mdiscoword :3 fatal: Failed to connect to server, \x1b[33m{e}\x1b[0m")
                    exit()

                document.derender()

                read_styles("message_layout_style.tss")
                read_vis("message_layout.vis")

                document = Globals.__vis_document__

                message_scrollbox: Scrollbox = document.get_element_by_id("messages_pane")
                message_input: Input = document.get_element_by_id("message_send_input")

                def on_send_msg(content: str):
                    """
                    Creates a Message component, adds it to the chat history, and rerenders the chat history.
                    """
                    element = Message(content)
                    message_scrollbox.add_child(element)
                    message_scrollbox.scroll_to_bottom()
                    message_scrollbox.render()

                def on_enter(element: Input):
                    """
                    event handler for when the message input is submitted.
                    """
                    curr_text = element.curr_text
                    on_send_msg(curr_text)
                    element.clear()

                message_input.on_enter = on_enter
                test.on_messages_screen = True

                document.mount()
                break

        document.listener_thread.join()

if __name__ == "__main__":
    with Globals.__vis_document__.term.hidden_cursor(), Globals.__vis_document__.term.raw():
        main()
