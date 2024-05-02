from interpreter import read_styles, read_vis
from globalvars import Globals
from logger import Logger
from utils import cls, hide_cursor, show_cursor
from div import Div
from text import Text
from scrollbox import Scrollbox
from input import Input
from button import Button
from threading import Thread

import requests
import socket
import uuid
<<<<<<< HEAD
<<<<<<< HEAD
||||||| parent of 66d64a6 (fix hiding cursor, create pixel font)
import json
=======
import json
from cursor import hide
>>>>>>> 66d64a6 (fix hiding cursor, create pixel font)

<<<<<<< HEAD
def main():
    read_styles("login_style.tss")
    read_vis("login_layout.vis")
||||||| parent of 732cb88 (setup message socket infrastructure)
read_styles("login_style.tss")
read_vis("login_layout.vis")

document = Globals.__vis_document__

container: "Div" = document.get_element_by_id("text_container")

username_input: "Input" = document.get_element_by_id("username-input")
password_input: "Input" = document.get_element_by_id("password-input")
submit_button: "Button" = document.get_element_by_id("submit-button")
error_message: "Text" = document.get_element_by_id("error_message")

class test:
    on_messages_screen = False

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
        error_message.text = "Couldn't connect to server!"
        error_message.render()

def submit_handler():
=======
read_styles("login_style.tss")
read_vis("login_layout.vis")

document = Globals.__vis_document__

container: "Div" = document.get_element_by_id("text_container")

username_input: "Input" = document.get_element_by_id("username-input")
password_input: "Input" = document.get_element_by_id("password-input")
submit_button: "Button" = document.get_element_by_id("submit-button")
error_message: "Text" = document.get_element_by_id("error_message")

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
>>>>>>> 732cb88 (setup message socket infrastructure)
    
    document = Globals.__vis_document__

<<<<<<< HEAD
    container: "Div" = document.get_element_by_id("text_container")
||||||| parent of 732cb88 (setup message socket infrastructure)
    data = res.json()
    
    if data['type'] == 'success':
        test.on_messages_screen = True  
=======
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
>>>>>>> 732cb88 (setup message socket infrastructure)

    username_input: "Input" = document.get_element_by_id("username-input")
    password_input: "Input" = document.get_element_by_id("password-input")
    submit_button: "Button" = document.get_element_by_id("submit-button")
    error_message: "Text" = document.get_element_by_id("error_message")

<<<<<<< HEAD
    class test:
        on_messages_screen = False
||||||| parent of 732cb88 (setup message socket infrastructure)
while True:
    if test.on_messages_screen:
=======
def send_message(content: str):
    mem.sock.send({
        "token": mem.token,
        "author": mem.username,
        "content": content,
    })
||||||| parent of f9e4bbf ([major] finish integration with local server)

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
=======
import json
>>>>>>> f9e4bbf ([major] finish integration with local server)

<<<<<<< HEAD
while True:
    if mem.on_messages_screen:
>>>>>>> 732cb88 (setup message socket infrastructure)

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
||||||| parent of f9e4bbf ([major] finish integration with local server)
def main():
    
    read_styles("login_style.tss")
    read_vis("login_layout.vis")

    document = Globals.__vis_document__

    container: "Div" = document.get_element_by_id("text_container")

    username_input: "Input" = document.get_element_by_id("username-input")
    password_input: "Input" = document.get_element_by_id("password-input")
    submit_button: "Button" = document.get_element_by_id("submit-button")
    error_message: "Text" = document.get_element_by_id("error_message")
=======
def main():
    
    document = Globals.__vis_document__
    container: "Div" = document.get_element_by_id("text_container")
    username_input: "Input" = document.get_element_by_id("username-input")
    password_input: "Input" = document.get_element_by_id("password-input")
    submit_button: "Button" = document.get_element_by_id("submit-button")
    error_message: "Text" = document.get_element_by_id("error_message")
>>>>>>> f9e4bbf ([major] finish integration with local server)

    class mem:
        on_messages_screen = False
        sock: socket.socket = None 

        token: str = None
        cache: str = None
        user_id: str = None
        username: str = None
        
        socket_listen_thread: Thread = None
        
        messages: list = []
        """ list of dicts, each dict is a message with 'author' and 'content' keys. """

    def Message(author: str, content: str) -> Div:
        """
        Generic message component with author name
        """
        return Div(
            class_str="message-obj",
            children=[
                Text(
                    class_str="message-obj-author",
                    text=f"@{author}"
                ),
                Text(
                    class_str="message-obj-content",
                    text=content
                ),
            ]
        )
        
    def MessageRedundant(content: str) -> Div:
        """
        Generic message component for when someone sends multiple messages in a row
        (no need to repeat the author name in this case)
        """
        return Div(
            class_str="message-obj-redundant",
            children=[
                Text(
                    class_str="message-obj-content-redundant",
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
        
        Logger.log(f"[submit handler] response json['type']: {data.get('type')} <- exception incoming if none")
        if data['type'] == 'success':
            
            mem.user_id = data['user_id']
            mem.token = data['token']
            mem.cache = data['cache']
            mem.username = data['username']
            
            Logger.log(f"login attempt successful! token={data['token']}")
            mem.on_messages_screen = True
            init_messages_socket()

        elif data['type'] == 'invalid':
            Logger.log(f"login attempt invalid! (wrong user/pass)")
            error_message.text = "Incorrect credentials!"
        else: 
            Logger.log(f"login attempt failed! (server err or smth)")
            error_message.text = "Failed to log in (A)! Try again later."
            
        error_message.render()

    def init_messages_socket():
        # set up message socket
            mem.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mem.sock.connect(("127.0.0.1", 5001))
            # immediately send our token
            Logger.log(f"sending token: {mem.token}")
            mem.sock.send(mem.token.encode())

            def socket_listen_loop():
                while True:
                    try:
                        data = mem.sock.recv(1024)
                    except:
                        # probably a disconnect
                        document.quit_app(f"Disconnected from server, i think...")
                    if not data:
                        continue
                    
                    # data sent from server is a dict of the following form:
                    # {
                    #     "author": str
                    #     "content": str
                    # }
                    # this gets stringified and set over, so we first decode it and then parse it.
                    
                    message = json.loads(data.decode())
                    
                    # now create a new message element and add it to the scrollbox
                    
                    # check author of the latest message - if its the same as this author, use a messageRedundant element
                                        
                    element = (
                        Message(message['author'], message['content']) if not mem.messages or mem.messages[-1]['author'] != message['author']
                        else MessageRedundant(message['content'])
                    )
                    message_scrollbox.add_child(element)
                    message_scrollbox.scroll_to_bottom()
                    message_scrollbox.render()
                    
                    # add message to cache
                    mem.messages.append(message)

            # start the listener thread
            mem.socket_listen_thread = Thread(target=socket_listen_loop)
            mem.socket_listen_thread.start()

    def send_message(content: str):
        mem.sock.send(json.dumps({
            "token": mem.token,
            "author": mem.username,
            "content": content,
        }).encode())
        Logger.log(f"sent message, {content=}")

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

<<<<<<< HEAD
            def on_send_msg(content: str):
                """
                Creates a Message component, adds it to the chat history, and rerenders the chat history.
                """
                element = Message(content)
                message_scrollbox.add_child(element)
                message_scrollbox.scroll_to_bottom()
                message_scrollbox.render()
||||||| parent of f9e4bbf ([major] finish integration with local server)
                # setup socket
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(("localhost", 5000))
                except Exception as e:
                    cls()
                    print(f"\x1b[31mdiscoword :3 fatal: Failed to connect to server, \x1b[33m{e}\x1b[0m")
                    exit()
=======
            def on_enter(element: Input):
                """
                base event handler that is given to the message input element.
                """
                curr_text = element.curr_text
                send_message(curr_text) # send message to server
                element.clear()
>>>>>>> f9e4bbf ([major] finish integration with local server)

<<<<<<< HEAD
            def on_enter(element: Input):
                """
                event handler for when the message input is submitted.
                """
                curr_text = element.curr_text
                on_send_msg(curr_text)
                element.clear()
||||||| parent of f9e4bbf ([major] finish integration with local server)
                document.derender()
=======
            message_input.on_enter = on_enter
            mem.on_messages_screen = True
>>>>>>> f9e4bbf ([major] finish integration with local server)

<<<<<<< HEAD
            message_input.on_enter = on_enter
            test.on_messages_screen = True
||||||| parent of f9e4bbf ([major] finish integration with local server)
                read_styles("message_layout_style.tss")
                read_vis("message_layout.vis")
=======
            Logger.log(f"mem.on_messages_screen: {mem.on_messages_screen}, second mount inc!")
            document.mount()
            break
>>>>>>> f9e4bbf ([major] finish integration with local server)

<<<<<<< HEAD
            document.mount()
            break

    document.listener_thread.join()
||||||| parent of f9e4bbf ([major] finish integration with local server)
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
=======
    # while loop finishing means on messages screen
    # for now just join with keylistener thread (since it stops when user presses exit key)
    document.listener_thread.join()
>>>>>>> f9e4bbf ([major] finish integration with local server)

if __name__ == "__main__":

    hide()
    
    read_styles("login_style.tss")
    read_vis("login_layout.vis")
    
    with Globals.__vis_document__.term.cbreak():
        try:
            main()
            show_cursor()
        except Exception as e:
            Logger.log(f"EXCEPTION IN MAIN: {e}")
            Logger.write()
            cls()
            print(f"\x1b[31mdiscoword :3 fatal: an error occurred, \x1b[33m{e}\x1b[0m")
            exit()
