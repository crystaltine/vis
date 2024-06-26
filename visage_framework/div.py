from element import Element
from utils import fcode, convert_to_chars, print3
from typing import List, Unpack
from globalvars import Globals
from logger import Logger
from boundary import Boundary
from time import time

class Div(Element):
    """
    A general div class with customizable styling options.
    """
    
    class Attributes(Element.Attributes):
        id: str | None
        class_str: str | None
        style_str: str | None
        children: List["Element"]
    
    class StyleProps(Element.StyleProps):
        """ A schema of style options for divs. """
        position: str
        visible: bool
        left: str
        top: str
        width: str
        height: str
        padding_top: int
        padding_right: int
        padding_bottom: int
        padding_left: int
        padding: int
        bg_color: str | tuple
    
    SUPPORTS_CHILDREN = True
    DEFAULT_STYLE: "Div.StyleProps" = {
        "position": "relative",
        "visible": True,
        "left": "0%",
        "top": "0%",
        "width": "100%",
        "height": "100%",
        "padding_top": 0,
        "padding_right": 0,
        "padding_bottom": 0,
        "padding_left": 0,
        "padding": 0,
        "bg_color": (255, 255, 255), # can be hex code, rgb tuple, or 'transparent'
    }

    def __init__(self, **attrs: Unpack["Attributes"]):
        """
        Attributes:
        - id: str | None
        - class_str: str | None
        - style_str: str | None
        - children: List["Element"]
        """
        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        
        self.children: List["Element"] = attrs.get("children", [])
        #Logger.log(f"{self}'s children on init: {self.children}")
    
    def render(self, container_bounds: Boundary = None, container_bg: str = None):

        #Logger.log(f"<BEGIN DIV render func>")
        #Logger.log(f"Div render params: {container_bounds.left=} {container_bounds.top=} {container_bounds.right=} {container_bounds.bottom=}")
        container_bounds = self.get_true_container_edges(container_bounds)
        Boundary.set_client_boundary(self, container_bounds)
        curr_bg_color = self.getset_curr_bg_color(container_bg)
        
        #Logger.log(f"Div (id={self.id}) given top: {self.style.get('top')}, bottom: {self.style.get('bottom')}, height: {self.style.get('height')}, calced client_top={self.client_top}, client_bottom={self.client_bottom}, client_height={self.client_height}")
        #Logger.log(f"^ {container_bounds.top=}, {container_bounds.bottom=}, {container_height=}")
        
        if not self.style.get("visible"): return
        
        #Logger.log(f"[t={time()}]: about to print some random stuff from div render()")
        #print(f"{Globals.__vis_document__.term.move_xy(4, 4)}Div drawing bg, curr_bg_color is {curr_bg_color}")

        # draw the rectangle IF it is not transparent.
        if curr_bg_color != 'transparent':
            for i in range(self.client_top, self.client_bottom):
                #with Globals.__vis_document__.term.hidden_cursor():
                print3(Globals.__vis_document__.term.move_xy(self.client_left, i) + fcode(background=curr_bg_color) + " " * self.client_width + "\x1b[0m")
        
        # Logger.log(f"[t={time()}] div drawn, moving to children")
        
        # render children
        for child in self.children:
            
            if self is child: continue # ??? - for some reason using this func adds a self pointer to its own children. try fixing later
            
            # Logger.log(f"Div rendering children: cli_left, cli_top, cli_right, cli_bottom: {self.client_left=} {self.client_top=} {self.client_right=} {self.client_bottom=}")
            Logger.log(f"div with id={self.id} rendering child {type(child)} with id={child.id}")
            
            general_padding_x, general_padding_y = (convert_to_chars(self.client_width, self.style.get("padding")), convert_to_chars(self.client_height, self.style.get("padding"))) if self.style.get("padding") is not None else 0
            child.render(Boundary(
                self.client_left + convert_to_chars(self.client_width, self.style.get("padding_left")) or general_padding_x,
                self.client_top + convert_to_chars(self.client_height, self.style.get("padding_top")) or general_padding_y,
                self.client_right - convert_to_chars(self.client_width, self.style.get("padding_right")) or general_padding_x,
                self.client_bottom - convert_to_chars(self.client_height, self.style.get("padding_bottom")) or general_padding_y
            ), container_bg=curr_bg_color)
            
    def _render_partial(self, container_bounds: Boundary, max_bounds: Boundary, container_bg: str = None) -> None:
        # first do the same stuff as render
        container_bounds = self.get_true_container_edges(container_bounds)
        Boundary.set_client_boundary(self, container_bounds)
        curr_bg_color = self.getset_curr_bg_color(container_bg)
        
        if not self.style.get("visible"): return
        
            # if completely out of render, just skip all this goofy ah garbage
        if (
            max_bounds.left > self.client_right or
            max_bounds.right < self.client_left or 
            max_bounds.top > self.client_bottom or
            max_bounds.bottom < self.client_top
        ): return

        #Logger.log(f"[div] PARTIALRENDER: max top={max_bounds.top} max bot={max_bounds.bottom}")

        if curr_bg_color != 'transparent':
            #Logger.log(f"[div] PARTIALRENDER: drawing bg from max({self.client_top}, {max_bounds.top}) TO (min({self.client_bottom}, {max_bounds.bottom}))")
            for i in range(max(self.client_top, max_bounds.top), min(self.client_bottom+1, max_bounds.bottom)):
                # diagram:
                #  cli_left   bounds_left              bounds_right  cli_right
                #  |          |                        |             |
                #  --------------------------------------------------- = client_width
                #             -------------------------- = max_bounds.right - max_bounds.left
                #with Globals.__vis_document__.term.hidden_cursor():
                print3(Globals.__vis_document__.term.move_xy(max(self.client_left, max_bounds.left), i) + fcode(background=curr_bg_color) + " " * min(self.client_width, max_bounds.right - max_bounds.left))
                
        # render children
        for child in self.children:
            
            if self is child: continue # ??? - for some reason using this func adds a self pointer to its own children. try fixing later
            
            # Logger.log(f"Div rendering children: cli_left, cli_top, cli_right, cli_bottom: {self.client_left=} {self.client_top=} {self.client_right=} {self.client_bottom=}")
            
            general_padding_x, general_padding_y = (convert_to_chars(self.client_width, self.style.get("padding")), convert_to_chars(self.client_height, self.style.get("padding"))) if self.style.get("padding") is not None else 0
            child._render_partial(Boundary(
                self.client_left + convert_to_chars(self.client_width, self.style.get("padding_left")) or general_padding_x,
                self.client_top + convert_to_chars(self.client_height, self.style.get("padding_top")) or general_padding_y,
                self.client_right - convert_to_chars(self.client_width, self.style.get("padding_right")) or general_padding_x,
                self.client_bottom - convert_to_chars(self.client_height, self.style.get("padding_bottom")) or general_padding_y
            ), max_bounds, container_bg=curr_bg_color)
             
    def add_child(self, child: "Element", index: int = None):
        """
        Adds a child div at the specified index, which means where on the component tree it will be placed.
        If index is None, it will be added to the end of the list of children.
        
        @TODO - for some reason, this leads to a recursion error because objects get added all over the document. IDK why!!
        (probably pointer/inheritance issue)
        """
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
            
        #Logger.log(f"Added child to {self}: {child}")