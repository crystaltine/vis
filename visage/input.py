from element import Element
from utils import fcode, calculate_dim
from typing import Literal, TypedDict, Unpack, TYPE_CHECKING

if TYPE_CHECKING:
    from key_event import KeyEvent
    
class Input(Element):
    
    class Attributes(Element.Attributes):
        """ All special props that can be used for creating an input element. """
        placeholder: str | None
        
    class StyleProps(Element.StyleProps):
        """ A schema of style options for input elements. """
        position: str
        visible: bool
        color: str | tuple 
        placeholder_color: str | tuple
        bg_color: str | tuple
        bold: bool
        italic: bool
        underline: bool
        padding_top: int
        padding_right: int
        padding_bottom: int
        padding_left: int
        padding: int
        left: int
        right: int | None
        y: int
        text_align: Literal["left", "center", "right"]
        selectable: bool
        
    SUPPORTS_CHILDREN = False
    DEFAULT_STYLE: "Input.StyleProps" = {
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
        "selectable": True,
    }
    
    """
    Represents text that can be placed inside any element.
    """
    def __init__(self, **attrs: Unpack[InputElementAttributes]):
        
        super().__init__(**attrs)

        self.placeholder = attrs.get("placeholder", "")
        self.curr_text = ""
        self.cursor_pos = 0
        
        # assert that not both left and right are None
        assert not (self.style.left is None and self.style.right is None), "[Text]: At least one of left or right must not be None."

        def _event_handler(e: "KeyEvent"):
            """ Internal event handler for document keydown events (for typing inside the element) """
            if not self.selected: return

            # else, handle key.
            if not e.is_special:
                # add to curr_text if just regular char
                self.curr_text += e.key
            else:
                
                # TODO - create enum or some way to check special keys

                if e.key == 'backspace':
                    if not self.curr_text: return
                        self.curr_text = 
                    
                elif e.key == 'del':
                    if not self.curr_text: return

                elif e.key == 'enter':
                    # deselect everything
                    pass
                elif e.key == 'esc':
                    self.curr_text = ""
                    # return or something/deselect
                elif e.key == 'tab':
                    # deselect BUT go to next element
                    pass
                

        # register this element's event handler with the document's special handlers
        self.document.element_keydown_listeners[self] = set([_event_handler])

    def render(self, container_left: int, container_top: int, container_right: int, container_bottom: int):
        """
        Renders the input element to its container at the specified position, given the positions of the container.
        """
        
        container_left = container_left if self.style.position == "relative" else 0
        container_top = container_top if self.style.position == "relative" else 0
        container_right = container_right if self.style.position == "relative" else self.document.term.width
        container_bottom = container_bottom if self.style.position == "relative" else self.document.term.height
        
        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        # if curr text isn't empty, use it. otherwise, use placeholder
        text_len = len(self.curr_text or self.placeholder)
        
        # calculate text left position
        # precondition: at least one of left or right is not None (see `init`)
        if self.style.left is not None:
            self.client_left = container_left + calculate_dim(container_width, self.style.left) - (
                0 if self.style.text_align == "left" else
                text_len // 2 if self.style.text_align == "center" else
                text_len
            )
        else: # we can do this because precondition guarantees that right is not None if left is None
            self.client_left = container_left + calculate_dim(container_width, self.style.right) - text_len + (
                0 if self.style.text_align == "left" else
                text_len // 2 if self.style.text_align == "center" else
                text_len
            )
            
        # set client_... attributes just for info
        # self.client_left is already set
        self.client_right = self.client_left + text_len
        self.client_top = container_top + calculate_dim(container_height, self.style.y)
        self.client_bottom = self.client_top + 1
        
        if not self.style.visible: return
            
        style_string = " ".join([
            "bold" if self.style.bold else "",
            "italic" if self.style.italic else "",
            "underline" if self.style.underline else ""
        ])
        
        # if curr_text is empty, render placeholder instead
        text_to_render = (
            fcode(self.style.color, background=self.bg_color, style=style_string) + self.curr_text if self.curr_text
            else fcode(self.style.placeholder_color, background=self.bg_color, style=style_string) + self.placeholder
        )

        with self.document.term.hidden_cursor():
            print(self.document.term.move_xy(self.client_left, self.client_top) + text_to_render, end="")
