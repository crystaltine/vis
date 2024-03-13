# note - this is meant to be merged.
# on local state this doesn't match the rest of the code
# pls merge with home computer
# NOTE - require Element abc to have SELECTABLE and is_selected
# also add .selected to `Document`
# NOTE - check out typing.Unpack! allows specifying kwargs to functions

from common import ElementAttributes, Element
from utils import fcode, calculate_dim
from typing import Literal

class InputElementAttributes(ElementAttributes):
    placeholder: str | None
    
class Input(Element):
    
    SUPPORTS_CHILDREN = False
    DEFAULT_STYLE = {
        "position": "relative",
        "visible": True,
        "color": "black",
        "placeholder_color": "gray",
        "bg_color": "white",
        "bold": False,
        "italic": False,
        "underline": False,
        "padding_top": 0,
        "padding_right": 0,
        "padding_bottom": 0,
        "padding_left": 0,
        "padding": 0,
        "left": 0,
        "right": None, # calculated from "left" and text length
        "y": 0,
        "text_align": "left",
    }
    
    """
    Represents text that can be placed inside any element.
    """
    def __init__(self, attrs: InputElementAttributes):
        
        super().__init__(attrs)
        self.placeholder = attrs.get("placeholder", "")
        
        # assert that not both left and right are None
        assert not (self.left is None and self.right is None), "[Text]: At least one of left or right must not be None."

    def __event_handler__(self, key):
        """ Internal event handler for document keydown events (for typing inside the element) """
        if not self.selected: return


    def render(self, container_left: int, container_top: int, container_right: int, container_bottom: int):
        """
        Renders the input element to its container at the specified position, given the positions of the container.
        """
        
        container_left = container_left if self.position == "relative" else 0
        container_top = container_top if self.position == "relative" else 0
        container_right = container_right if self.position == "relative" else self.document.term.width
        container_bottom = container_bottom if self.position == "relative" else self.document.term.height
        
        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        text_len = len(self.text)
        
        # calculate text left position
        # precondition: at least one of left or right is not None (see `init`)
        if self.left is not None:
            self.client_left = container_left + calculate_dim(container_width, self.left) - (
                0 if self.text_align == "left" else
                text_len // 2 if self.text_align == "center" else
                text_len
            )
        else: # we can do this because precondition guarantees that right is not None if left is None
            self.client_left = container_left + calculate_dim(container_width, self.right) - text_len + (
                0 if self.text_align == "left" else
                text_len // 2 if self.text_align == "center" else
                text_len
            )
            
        # set client_... attributes just for info
        # self.client_left is already set
        self.client_right = self.client_left + text_len
        self.client_top = container_top + calculate_dim(container_height, self.y)
        self.client_bottom = self.client_top + 1
        
        if not self.visible: return
            
        style_string = " ".join([
            "bold" if self.bold else "",
            "italic" if self.italic else "",
            "underline" if self.underline else ""
        ])
        
        with self.document.term.hidden_cursor():
            print(self.document.term.move_xy(self.client_left, self.client_top) + fcode(self.color, background=self.bg_color, style=style_string) + self.text, end="")
