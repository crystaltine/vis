from element import Element
from utils import fcode, calculate_dim
from typing import Literal, Unpack, TYPE_CHECKING
from globalvars import Globals
from logger import Logger

if TYPE_CHECKING:
    from key_event import KeyEvent
    
class Input(Element):
    """
    An editable text field
    """
    
    class Attributes(Element.Attributes):
        """ All special props that can be used for creating an input element. """
        id: str | None
        class_str: str | None
        style_str: str | None
        placeholder: str | None
        max_len: int | None
        pattern: str | None
        
    class StyleProps(Element.StyleProps):
        """ A schema of style options for input elements. """
        position: str
        visible: bool
        color: str | tuple 
        placeholder_color: str | tuple
        bg_color: str | tuple
        hovered_bg_color: str | tuple
        selected_bg_color: str | tuple
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
        width: int
        y: int
        text_align: Literal["left", "center", "right"]
        hoverable: bool
        selectable: bool
        
    SUPPORTS_CHILDREN = False
    DEFAULT_STYLE: "StyleProps" = {
        "position": "relative",
        "visible": True,
        "color": "black",
        "placeholder_color": "gray",
        "bg_color": "white",
        "hovered_bg_color": (230, 230, 230),
        "selected_bg_color": (190, 190, 210),
        "bold": False,
        "italic": False,
        "underline": False,
        "padding_top": 0,
        "padding_right": 0,
        "padding_bottom": 0,
        "padding_left": 0,
        "padding": 0,
        "left": 0,
        "right": None,
        "width": 10,
        "y": 0,
        "text_align": "left",
        "hoverable": True,
        "selectable": True,
    }
    
    def __init__(self, **attrs: Unpack["Attributes"]):
        
        super().__init__(**attrs)

        self.placeholder = attrs.get("placeholder", "")
        self.max_len = attrs.get("max_len", None)
        self.curr_text = ""
        self.cursor_pos = 0

        self.text_left_index = 0
        """ Represents the index of the leftmost character to render, in case of overflow """
        
        # assert that not both left and right are None
        assert not (self.style.get("left") is None and self.style.get("right") is None), "[Text]: At least one of left or right must not be None."

        def _event_handler(e: "KeyEvent"):
            """ Internal event handler for document keydown events (for typing inside the element) """
            if not self.is_selected: return

            # else, handle key.
            if not e.is_special:
                # add to curr_text if just regular char
                Logger.log(f"Input: non-special key '{e.key}': curr text is now {self.curr_text}")
                if self.max_len is not None and len(self.curr_text) >= self.max_len:
                    return
                
                self.curr_text = self.curr_text[:self.cursor_pos] + e.key + self.curr_text[self.cursor_pos:]
                self.cursor_pos += 1
            else:
                if e.key == 'backspace':
                    # assertion: cursor_pos in [0, len(curr text)]
                    # thus, we need to clip cursor_pos-1 to 0
                    self.curr_text = self.curr_text[:max(0,self.cursor_pos-1)]+self.curr_text[self.cursor_pos:]
                    self.cursor_pos = max(0, self.cursor_pos - 1)

                elif e.key == 'del':
                    # assertion: cursor_pos in [0, len(curr text)]
                    # thus, we need to clip cursor_pos+1 to len(curr text)
                    self.curr_text = self.curr_text[:self.cursor_pos]+self.curr_text[min(len(self.curr_text),self.cursor_pos+1):]

                elif e.key == 'left':
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                
                elif e.key == 'right':
                    self.cursor_pos = min(len(self.curr_text), self.cursor_pos + 1)

                elif e.key == 'enter':
                    # deselect everything (TODO)
                    pass
                elif e.key == 'esc':
                    self.curr_text = ""
                    # return or something/deselect (same as enter) (TODO)
                elif e.key == 'tab':
                    # deselect BUT go to next element (TODO)
                    pass

                Logger.log(f"Input: special key {e.key}: curr_text is now {self.curr_text}, curs_pos is {self.cursor_pos}")
            
            self.render()

        # register this element's event handler with the document's special handlers
        Globals.__vis_document__.element_keydown_listeners[self] = set([_event_handler])
        if self.style.get("selectable"): Globals.__vis_document__.selectable_elements.add(self)
        if self.style.get("hoverable"): Globals.__vis_document__.hoverable_elements.add(self)

    def render(self, container_left: int = None, container_top: int = None, container_right: int = None, container_bottom: int = None):
        """
        Renders the input element to its container at the specified position, given the positions of the container.
        """

        if len(self.last_remembered_container) == 4:
            container_left = container_left or self.last_remembered_container[0]
            container_top = container_top or self.last_remembered_container[1]
            container_right = container_right or self.last_remembered_container[2]
            container_bottom = container_bottom or self.last_remembered_container[3]

        self.last_remembered_container = [container_left, container_top, container_right, container_bottom]
        
        container_left = container_left if self.style.get("position") == "relative" else 0
        container_top = container_top if self.style.get("position") == "relative" else 0
        container_right = container_right if self.style.get("position") == "relative" else Globals.__vis_document__.term.width
        container_bottom = container_bottom if self.style.get("position") == "relative" else Globals.__vis_document__.term.height

        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        # if curr text isn't empty, use it. otherwise, use placeholder
        text_len = len(self.curr_text or self.placeholder)
        
        # calculate text left position
        # precondition: at least one of left or right is not None (see `init`)
        if self.style.get("left") is not None:
            self.client_left = container_left + calculate_dim(container_width, self.style.get("left")) - (
                0 if self.style.get("text_align") == "left" else
                text_len // 2 if self.style.get("text_align") == "center" else
                text_len
            )
        else: # we can do this because precondition guarantees that right is not None if left is None
            self.client_left = container_left + calculate_dim(container_width, self.style.get("right")) - text_len + (
                0 if self.style.get("text_align") == "left" else
                text_len // 2 if self.style.get("text_align") == "center" else
                text_len
            )
            
        # set client_... attributes just for info
        # self.client_left is already set
        self.client_right = self.style.get("right") or self.client_left + calculate_dim(container_width, self.style.get("width"))
        self.client_top = container_top + calculate_dim(container_height, self.style.get("y"))
        self.client_bottom = self.client_top + 1
        
        if not self.style.get("visible"): return
        
        # =======================
        # TEXT RENDERING:
        # =======================

        style_string = " ".join([
            "bold" if self.style.get("bold") else "",
            "italic" if self.style.get("italic") else "",
            "underline" if self.style.get("underline") else ""
        ])
        bg_color_to_use = self.style.get(
            "bg_color" if (not self.is_selected and not self.is_hovered)
            else "hovered_bg_color" if (self.is_hovered and not self.is_selected)
            else "selected_bg_color"
        )
        regular_text_fcode = fcode(self.style.get("color"), background=bg_color_to_use, style=style_string)
        placeholder_fcode = fcode(self.style.get("placeholder_color"), background=bg_color_to_use, style=style_string)

        visible_curr_text = self.curr_text[self.text_left_index:min(self.text_left_index + self.client_right - self.client_left]

        # if curr_text is empty, render placeholder instead
        text_to_render = (
            fcode(self.style.get("color"), background=bg_color_to_use, style=style_string) + self.visible_curr_text if self.curr_text
            else fcode(self.style.get("placeholder_color"), background=bg_color_to_use, style=style_string) + self.placeholder
        )

        with Globals.__vis_document__.term.hidden_cursor():
            print(Globals.__vis_document__.term.move_xy(self.client_left, self.client_top) + " "*self.style.get("width")
            print(Globals.__vis_document__.term.move_xy(self.client_left, self.client_top) + text_to_render, end="")
