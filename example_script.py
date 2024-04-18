from interpreter import read_styles, read_vis
from globalvars import Globals
from div import Div
from text import Text
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrollbox import Scrollbox
    from input import Input

read_styles("message_layout_style.tss")
read_vis("message_layout.vis")

document = Globals.__vis_document__
document.mount()

# dont care about resize for now, too complicated to optimize lol

message_scrollbox: Scrollbox = document.get_element_by_id("messages_pane")
message_input: Input = document.get_element_by_id("message_send_input")
num_messages_sent = 0

def Message(content: str) -> Div:
    """
    Generic message component
    """
    return Div(
        id=f"message-{num_messages_sent}",
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

def on_send_msg(content: str):
    element = Message(content)
    message_scrollbox.add_child(element)
    message_scrollbox.scroll_to_bottom()
    message_scrollbox.render()

def on_enter(element: Input):
    curr_text = element.curr_text
    on_send_msg(curr_text)
    element.clear()

message_input.on_enter = on_enter