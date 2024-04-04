from element import Element
from utils import fcode, convert_to_chars
from typing import List, Unpack
from globalvars import Globals
from logger import Logger

class Scrollbox(Element):
    """
    A div-like element, meant to be a container, auto-positions children.
    For now, auto-positions elements vertically.
    Children should have:
    - width (default 100% if unspecified)
    - height: must be specified. If in percents, 
    """
    
    class Attributes(Element.Attributes):
        id: str | None
        class_str: str | None
        style_str: str | None
        children: List["Element"]
    
    class StyleProps(Element.StyleProps):
        """ A schema of style options for scrollboxes. """
        position: str
        visible: bool
        left: str
        top: str
        width: str
        height: str
        right: str
        bottom: str
        bg_color: str | tuple
    
    SUPPORTS_CHILDREN = True
    DEFAULT_STYLE: "Scrollbox.StyleProps" = {
        "position": "relative",
        "visible": True,
        "left": "0%",
        "top": "0%",
        "width": "100%",
        "height": "100%",
        "right": None, # calculated from "left" and "width"
        "bottom": None, # calculated from "top" and "height"
        "bg_color": (255, 255, 255), # can be hex code, rgb tuple, or 'transparent'
    }

    def __init__(self, **attrs: Unpack["Attributes"]):        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        
        # assert that ONE of left/right and ONE of top/bottom is provided
        assert (self.style.get("left") is not None or self.style.get("right") is not None), "[Scrollbox]: At least one of left or right must not be None."
        assert (self.style.get("top") is not None or self.style.get("bottom") is not None), "[Scrollbox]: At least one of top or bottom must not be None."
        
        self.scroll_y = 0
        """ Represents the number of characters scrolled from the top. 0 means we are at the top, 1 would mean we are scrolled down by 1 char, etc. """
        
        self.children: List["Element"] = attrs.get("children", [])
        
        self._bg_fcode = fcode(background=self.style.get("bg_color")) if self.style.get("bg_color") != "transparent" else None
        
        # TODO - create/register event handler for when this element is active: up and down arrows scroll.
    
    def get_fully_rendered_children(self) -> List["Element"]:
        """
        Returns a list of children that can be fully rendered within the scrollbox,
        given the current scrollY, each element's height, and the current client height.
        
        IMPORTANT: `self.client_height` MUST be defined before calling this.
        """
        # create a prefix sum array of the heights of the tops of each child
        child_bottoms = [0]
        for i in range(len(self.children)):
            child_bottoms.append(child_bottoms[-1] + convert_to_chars(self.client_height, self.children[i].style.get("height")))
            
        # remove leading 0
        child_bottoms.pop(0)
        
        # now we go the first number in this (sorted) list that is greater than scrollY
        # and go until the last number that is NOT greater than scrollY + client_height
        # all numbers in between are the indices of the children that can be fully rendered.
        
        # find the first index that is greater than scrollY
        start_idx = 0
        for i in range(len(child_bottoms)):
            
    
    def render(self, container_left: int = None, container_top: int = None, container_right: int = None, container_bottom: int = None):

        Logger.log(f"\n<Begin Scrollbox render func>")
        Logger.log(f"Scrollbox render params: {container_left=} {container_top=} {container_right=} {container_bottom=}")
        container_left, container_top, container_right, container_bottom = self.get_true_container_edges(container_left, container_top, container_right, container_bottom)
        
        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        self.client_top = container_top + (convert_to_chars(container_height, self.style.get("top")) if self.style.get("top") is not None
            else container_bottom - convert_to_chars(container_height, self.style.get("bottom")) - convert_to_chars(container_height, self.style.get("height")))
        self.client_bottom = (container_bottom - convert_to_chars(container_height, self.style.get("bottom")) if self.style.get("bottom") is not None
            else container_top + convert_to_chars(container_height, self.style.get("top")) + convert_to_chars(container_height, self.style.get("height")))
        
        self.client_left = container_left + (convert_to_chars(container_width, self.style.get("left")) if self.style.get("left") is not None
            else container_right - convert_to_chars(container_width, self.style.get("right")) - convert_to_chars(container_width, self.style.get("width")))
        self.client_right = (container_right - convert_to_chars(container_width, self.style.get("right")) if self.style.get("right") is not None
            else container_left + convert_to_chars(container_width, self.style.get("left")) + convert_to_chars(container_width, self.style.get("width")))
        
        self.client_width = self.client_right - self.client_left 
        self.client_height = self.client_bottom - self.client_top
        
        #Logger.log(f"Scrollbox (id={self.id}) given top: {self.style.get('top')}, bottom: {self.style.get('bottom')}, height: {self.style.get('height')}, calced client_top={self.client_top}, client_bottom={self.client_bottom}, client_height={self.client_height}")
        #Logger.log(f"^ container top: {container_top}, bottom: {container_bottom}, height: {container_height}")
        
        if not self.style.get("visible"): return
        
        # draw the rectangle IF it is not transparent.
        if self._bg_fcode:
            for i in range(self.client_top, self.client_bottom):
                with Globals.__vis_document__.term.hidden_cursor():
                    print(Globals.__vis_document__.term.move_xy(self.client_left, i) + self._bg_fcode + " " * self.client_width, end="")
                    
        # render children
        Logger.log(f"\n<Scrollbox render func: child rendering:>")
        for child in self.children:
            
            if self is child: continue # ??? - for some reason using this func adds a self pointer to its own children. try fixing later
            
            Logger.log(f"Scrollbox rendering children: cli_left, cli_top, cli_right, cli_bottom: {self.client_left=} {self.client_top=} {self.client_right=} {self.client_bottom=}")
            
            general_padding = convert_to_chars(container_width, self.style.get("padding")) if self.style.get("padding") is not None else 0
            
            child.render(
                self.client_left + convert_to_chars(container_width, self.style.get("padding_left")) or general_padding,
                self.client_top + convert_to_chars(container_height, self.style.get("padding_top")) or general_padding,
                self.client_right - convert_to_chars(container_width, self.style.get("padding_right")) or general_padding,
                self.client_bottom - convert_to_chars(container_height, self.style.get("padding_bottom")) or general_padding
            )
             
    def add_child(self, child: "Element", index: int = None):
        """
        Adds a child at the specified index. IMPORTANT: index matters specifically for this element!
        Indices near 0 are placed near the top, indices near the end are placed near the bottom.
        
        If `index` is None, it will be added to the end of the list of children.
        """
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)