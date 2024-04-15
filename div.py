from element import Element
from utils import fcode, convert_to_chars
from typing import List, Unpack
from globalvars import Globals
from logger import Logger
from boundary import Boundary

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
        right: str
        bottom: str
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
        "right": None, # calculated from "left" and "width"
        "bottom": None, # calculated from "top" and "height"
        "padding_top": 0,
        "padding_right": 0,
        "padding_bottom": 0,
        "padding_left": 0,
        "padding": 0,
        "bg_color": (255, 255, 255), # can be hex code, rgb tuple, or 'transparent'
    }

    def __init__(self, **attrs: Unpack["Attributes"]):
        """ Keyword arguments: see `Div.Attributes`.
        Note: For style options that conflict, such as "top"/"bottom" and "height", the ones listed higher
        in the default dict above take precedence. Specifically, for dimensions/positioning, here are the rules:
        
        - if both top and bottom are provided, height is completely ignored.
        - if one of top or bottom, and height, are provided, the other top/bottom position is calculated from the height.
        - this is true for left/right/width as well.
        - therefore, at least two of the three positioning params for each dimension must be not None.
        
        (don't worry about not setting options, they have default values. Just don't set more than one of the
        position options (height/top/bottom, width/left/right) explicitly to None.
        
        Provide either percents or characters for the dimension values.
        Percents must be expressed as strings, e.g. '50%'. Characters can
        be either raw numbers or strings ending in 'ch', e.g. 50 or '50ch'.
        """
        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        
        # assert that ONE of left/right and ONE of top/bottom is provided
        assert (self.style.get("left") is not None or self.style.get("right") is not None), "[Div]: At least one of left or right must not be None."
        assert (self.style.get("top") is not None or self.style.get("bottom") is not None), "[Div]: At least one of top or bottom must not be None."
        
        self.children: List["Element"] = attrs.get("children", [])
        self._bg_fcode = fcode(background=self.style.get("bg_color")) if self.style.get("bg_color") != "transparent" else None
        #Logger.log(f"{self}'s children on init: {self.children}")
    
    def render(self, container_bounds: Boundary):

        #Logger.log(f"<BEGIN DIV render func>")
        #Logger.log(f"Div render params: {container_bounds.left=} {container_bounds.top=} {container_bounds.right=} {container_bounds.bottom=}")
        container_bounds = self.get_true_container_edges(container_bounds)
        
        Boundary.set_client_boundary(self, container_bounds)
        
        #Logger.log(f"Div (id={self.id}) given top: {self.style.get('top')}, bottom: {self.style.get('bottom')}, height: {self.style.get('height')}, calced client_top={self.client_top}, client_bottom={self.client_bottom}, client_height={self.client_height}")
        #Logger.log(f"^ {container_bounds.top=}, {container_bounds.bottom=}, {container_height=}")
        
        if not self.style.get("visible"): return
        
        # draw the rectangle IF it is not transparent.
        if self._bg_fcode:
            for i in range(self.client_top, self.client_bottom):
                with Globals.__vis_document__.term.hidden_cursor():
                    #Logger.log(f"drawing strip of div (id={self.id}) at y={i}")
                    print(Globals.__vis_document__.term.move_xy(self.client_left, i) + self._bg_fcode + " " * self.client_width, end="")
                    
        # render children
        for child in self.children:
            
            if self is child: continue # ??? - for some reason using this func adds a self pointer to its own children. try fixing later
            
            # Logger.log(f"Div rendering children: cli_left, cli_top, cli_right, cli_bottom: {self.client_left=} {self.client_top=} {self.client_right=} {self.client_bottom=}")
            
            general_padding_x, general_padding_y = (convert_to_chars(self.client_width, self.style.get("padding")), convert_to_chars(self.client_height, self.style.get("padding"))) if self.style.get("padding") is not None else 0
            
            child.render(Boundary(
                self.client_left + convert_to_chars(self.client_width, self.style.get("padding_left")) or general_padding_x,
                self.client_top + convert_to_chars(self.client_height, self.style.get("padding_top")) or general_padding_y,
                self.client_right - convert_to_chars(self.client_width, self.style.get("padding_right")) or general_padding_x,
                self.client_bottom - convert_to_chars(self.client_height, self.style.get("padding_bottom")) or general_padding_y
            ))
            
    def _render_partial(self, container_bounds: Boundary, max_bounds: Boundary) -> None:
        
        # first do the same stuff as render
        container_bounds = self.get_true_container_edges(container_bounds)
        Boundary.set_client_boundary(self, container_bounds)
        
        if not self.style.get("visible"): return
        
        if self._bg_fcode:
            for i in range(max(self.client_top, max_bounds.top), min(self.client_bottom, max_bounds.bottom)):
                with Globals.__vis_document__.term.hidden_cursor():
                    # diagram:
                    #  cli_left   bounds_left              bounds_right  cli_right
                    #  |          |                        |             |
                    #  --------------------------------------------------- = client_width
                    #             -------------------------- = max_bounds.right - max_bounds.left
                    print(Globals.__vis_document__.term.move_xy(max(self.client_left, max_bounds.left), i) + self._bg_fcode + " " * min(self.client_width, max_bounds.right - max_bounds.left), end="")
                    
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
            ), max_bounds)
             
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