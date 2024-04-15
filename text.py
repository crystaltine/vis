from element import Element
from utils import fcode, convert_to_chars
from typing import Literal, Unpack
from globalvars import Globals
from logger import Logger
from boundary import Boundary

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
        A typeddict of style options for text. No `top` or `bottom` because one line only.
        
        Left overrides right (if both not None, `right` is ignored). Cannot have both set to None.
        """
        position: str
        visible: bool
        color: str | tuple 
        bg_color: str | tuple
        bold: bool
        italic: bool
        underline: bool
        left: int | None
        right: int | None
        top: int | None
        bottom: int | None
        width: int | None
        height: int | None
    
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
        "right": None, # defaults to 100% width
        "width": "100%",
        "top": 0,
        "bottom": None, # auto based on top & how many lines the text takes up
        "height": None, # auto based on text length
        "wrap": True,
    }
    
    def __init__(self, **attrs: Unpack["Attributes"]):
        """ Keyword arguments: see `Text.Attributes`. """
        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        self.text = attrs.get("text", "")
        
        # assert that not both left and right are None
        assert (self.style.get("left") is not None or self.style.get("right") is not None), "[Text]: At least one of left or right must not be None."
        # assert that not both top and bottom are None
        assert (self.style.get("top") is not None or self.style.get("bottom") is not None), "[Text]: At least one of top or bottom must not be None."
        
    def render(self, container_bounds: Boundary):
        """
        Renders the text to its container at the specified position, given the positions of the container.
        """

        container_bounds = self.get_true_container_edges(container_bounds)

        # calculate width-related attributes
        l = self.style.get("left")
        r = self.style.get("right")
        container_width = container_bounds.right - container_bounds.left
        true_l = convert_to_chars(container_width, l)
        true_r = convert_to_chars(container_width, r)
        true_w = convert_to_chars(container_width, self.style.get("width"))
        self.client_left = container_bounds.left + (true_l if l is not None else container_bounds.right - true_r - true_w)
        self.client_right = container_bounds.right - true_r if r is not None else container_bounds.left + true_l + true_w       
        self.client_width = self.client_right - self.client_left 
        
        # calculate height in a special way IF:
        # top not None, bottom None, height None
        # or bottom not None, top None, height None
        # we assume client_width is fixed
        if self.style.get("height") is None:
            if self.style.get("top") is not None and self.style.get("bottom") is None:
                self.client_top = container_bounds.top + convert_to_chars(container_bounds.bottom - container_bounds.top, self.style.get("top"))
                # calculate height if wrap, otherwise just 1 line of text
                self.client_height = (len(self.text) // self.client_width + 1) if self.style.get("wrap") else 1
                self.client_bottom = self.client_top + self.client_height
            elif self.style.get("bottom") is not None and self.style.get("top") is None:
                self.client_bottom = container_bounds.bottom - convert_to_chars(container_bounds.bottom - container_bounds.top, self.style.get("bottom"))
                # calculate height if wrap, otherwise just 1 line of text
                self.client_height = (len(self.text) // self.client_width + 1) if self.style.get("wrap") else 1
                self.client_top = self.client_bottom - self.client_height                
                
        if not self.style.get("visible"): return
            
        style_string = " ".join([
            "bold" if self.style.get("bold") else "",
            "italic" if self.style.get("italic") else "",
            "underline" if self.style.get("underline") else ""
        ])
        
        with Globals.__vis_document__.term.hidden_cursor():
            print(Globals.__vis_document__.term.move_xy(self.client_left, self.client_top) + fcode(self.style.get("color"), background=self.style.get("bg_color"), style=style_string) + self.text, end="")
