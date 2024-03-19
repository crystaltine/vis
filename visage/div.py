from element import Element
from utils import fcode, calculate_dim
from typing import List, Unpack, TypedDict

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
        hoverable: bool
        selectable: bool
    
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
        "hoverable": False,
        "selectable": False,
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
        assert (self.style.left is not None or self.style.right is not None), "[Div]: At least one of left or right must not be None."
        assert (self.style.top is not None or self.style.bottom is not None), "[Div]: At least one of top or bottom must not be None."
        
        self.children: List["Element"] = attrs.get("children", [])
        self._bg_fcode = fcode(background=self.style.bg_color) if self.style.bg_color != "transparent" else None
        #Logger.log(f"{self}'s children on init: {self.children}")
    
    def render(self, container_left: int, container_top: int, container_right: int, container_bottom: int):

        #Logger.log(f"{self}'s children on render: {self.children}")
        
        container_left = container_left if self.style.position == "relative" else 0
        container_top = container_top if self.style.position == "relative" else 0
        container_right = container_right if self.style.position == "relative" else self.document.term.width
        container_bottom = container_bottom if self.style.position == "relative" else self.document.term.height
        
        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        self.client_top = container_top + (calculate_dim(container_height, self.style.top) if self.style.top 
            else calculate_dim(container_height, self.style.bottom) - calculate_dim(container_height, self.height))
        
        self.client_bottom = container_top + (calculate_dim(container_height, self.style.bottom) if self.style.bottom
            else calculate_dim(container_height, self.style.top) + calculate_dim(container_height, self.height))
        
        self.client_height = self.client_bottom - self.client_top
        
        self.client_left = container_left + (calculate_dim(container_width, self.style.left) if self.style.left
            else calculate_dim(container_width, self.style.right) - calculate_dim(container_width, self.width))
        
        self.client_right = container_left + (calculate_dim(container_width, self.style.right) if self.style.right
            else calculate_dim(container_width, self.style.left) + calculate_dim(container_width, self.width))
        
        self.client_width = self.client_right - self.client_left
        
        if not self.style.visible: return
        
        # draw the rectangle IF it is not transparent.
        if self._bg_fcode:
            for i in range(self.client_top, self.client_bottom):
                with self.document.term.hidden_cursor():
                    print(self.document.term.move_xy(self.client_left, i) + self._bg_fcode + " " * self.client_width, end="")
                    
        # render children
        for child in self.children:
            
            if self is child: continue # ??? - for some reason using this func adds a self pointer to its own children. try fixing later
            
            child.render(
                self.client_left + self.style.padding_left or self.style.padding or 0,
                self.client_top + self.style.padding_top or self.style.padding or 0,
                self.client_right - self.style.padding_right or self.style.padding or 0,
                self.client_bottom - self.style.padding_bottom or self.style.padding or 0
            )
             
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