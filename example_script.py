from interpreter import read_styles, read_vis
from globalvars import Globals
from div import Div
from text import Text
from scrollbox import Scrollbox
from input import Input
    

read_styles("message_layout_style.tss")
read_vis("message_layout.vis")

document = Globals.__vis_document__

# dont care about resize for now, too complicated to optimize lol

message_scrollbox: Scrollbox = document.get_element_by_id("messages_pane")
message_input: Input = document.get_element_by_id("message_send_input")

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

document.mount()