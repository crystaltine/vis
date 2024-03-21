from element import Element
from utils import fcode, calculate_dim
from typing import Literal, Unpack
from globalvars import Globals

class Text(Element):
    """
    Leaf-level element that renders stylable text.
    """
    
    class Attributes(Element.Attributes):
        id: str | None
        class_str: str | None
        style_str: str | None
        text: str
    
    class StyleProps(Element.StyleProps):
        """
        A schema of style options for text. No `top` or `bottom` because one line only.
        
        Left overrides right (if both not None, `right` is ignored). Cannot have both set to None.
        """
        position: str
        visible: bool
        color: str | tuple 
        bg_color: str | tuple
        bold: bool
        italic: bool
        underline: bool
        left: int
        right: int | None
        y: int
        text_align: Literal["left", "center", "right"]
        hoverable: bool
        selectable: bool
    
    SUPPORTS_CHILDREN = False
    DEFAULT_STYLE: "Text.StyleProps" = {
        "position": "relative",
        "visible": True,
        "color": "white",
        "bg_color": "transparent",
        "bold": False,
        "italic": False,
        "underline": False,
        "left": 0,
        "right": None, # calculated from "left" and text length
        "y": 0,
        "text_align": "left",
        "hoverable": False,
        "selectable": False,
    }
    
    def __init__(self, **attrs: Unpack["Attributes"]):
        """ Keyword arguments: see `Text.Attributes`. """
        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        self.text = attrs.get("text", "")
        
        # assert that not both left and right are None
        assert (self.style.get("left") is not None or self.style.get("right") is not None), "[Text]: At least one of left or right must not be None."
        
    def render(self, container_left: int = None, container_top: int = None, container_right: int = None, container_bottom: int = None):
        """
        Renders the text to its container at the specified position, given the positions of the container.
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
        
        text_len = len(self.text)
        
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
        self.client_right = self.client_left + text_len
        self.client_top = container_top + calculate_dim(container_height, self.style.get("y"))
        self.client_bottom = self.client_top + 1
        
        if not self.style.get("visible"): return
            
        style_string = " ".join([
            "bold" if self.style.get("bold") else "",
            "italic" if self.style.get("italic") else "",
            "underline" if self.style.get("underline") else ""
        ])
        
        with Globals.__vis_document__.term.hidden_cursor():
            print(Globals.__vis_document__.term.move_xy(self.client_left, self.client_top) + fcode(self.style.get("color"), background=self.style.get("bg_color"), style=style_string) + self.text, end="")
