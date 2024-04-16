from element import Element
from utils import fcode, convert_to_chars, indexof_first_larger_than
from typing import List, Tuple, Unpack
from globalvars import Globals
from logger import Logger
from boundary import Boundary
from copy import deepcopy

class Scrollbox(Element):
    """
    A div-like element, meant to be a container, auto-positions children.
    For now, auto-positions elements vertically.
    Children should have:
    - width (default 100% if unspecified)
    - height: must be specified. If in percents, calculated as proportion of REMAINING height
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
        bg_color: str | tuple
    
    SUPPORTS_CHILDREN = True
    DEFAULT_STYLE: "Scrollbox.StyleProps" = {
        "position": "relative",
        "visible": True,
        "left": "0%",
        "top": "0%",
        "width": "100%",
        "height": "100%",
        "bg_color": (255, 255, 255), # can be hex code, rgb tuple, or 'transparent'
    }

    def __init__(self, **attrs: Unpack["Attributes"]):        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        
        self.scroll_y = 0
        """ Represents the number of characters scrolled from the top. 0 means we are at the top, 1 would mean we are scrolled down by 1 char, etc. """
        
        self.children: List["Element"] = attrs.get("children", [])
        
        self._bg_fcode = fcode(background=self.style.get("bg_color")) if self.style.get("bg_color") != "transparent" else None
        
        # TODO - create/register event handler for when this element is active: up and down arrows scroll.
    
    def get_fully_rendered_child_range(self) -> Tuple[int, int]:
        """
        Returns a tuple [start, end] where start is the index of the first child that is fully rendered
        and end is 1+ the index of the last child that is fully rendered, based on the current scroll position.
        """
        
        if len(self.children) == 0: return (0, 0)

        child_edges = [0]
        for child in self.children:
            child_edges.append(child_edges[-1] + convert_to_chars(self.client_height, child.style.get("height")))
        
        # algorithm:
        # (child_edges is sorted)
        # let a be the index of the first number in child_edges which is greater than scrollY
        # let b be the index of the first number in child_edges which is greater than scrollY + client_height
        
        # top partially visible child is a-1
        # fully rendered children from a -> b-2
        # bottom partially visible child is b-1
        
        a = indexof_first_larger_than(child_edges, self.scroll_y)
        b = indexof_first_larger_than(child_edges, self.scroll_y + self.client_height)
        
        return (a, b-1)
    
    def render(self, container_bounds: Boundary):

        container_bounds = self.get_true_container_edges(container_bounds)
        Boundary.set_client_boundary(self, container_bounds)

        if not self.style.get("visible"): return
        
        # draw the rectangle IF it is not transparent.
        if self._bg_fcode:
            for i in range(self.client_top, self.client_bottom):
                with Globals.__vis_document__.term.hidden_cursor():
                    print(Globals.__vis_document__.term.move_xy(self.client_left, i) + self._bg_fcode + " " * self.client_width, end="")
                    
        # scrollbox child rendering
        Logger.log(f"\n<Scrollbox render func: child rendering:>")

        full_render_range = self.get_fully_rendered_child_range()
        first_partially_rendered = self.children[full_render_range[0]-1] if full_render_range[0]-1 >= 0 else None
        last_partially_rendered = self.children[full_render_range[1]+1] if full_render_range[1]+1 < len(self.children) else None

        current_bottommost = 0
        """ Where the client_bottom of the last rendered element is, absolute (relative to top of screen) """

        # use this as container_bounds. update .top and .bottom after every element render
        content_boundary = Boundary(self.client_left, self.client_top-self.scroll_y, self.client_right, self.client_bottom)
        # use this as max_bounds
        limit_boundary = Boundary(self.client_left, self.client_top, self.client_right, self.client_bottom)

        # rendering the top child
        if first_partially_rendered is not None:
            first_partially_rendered._render_partial(deepcopy(content_boundary), deepcopy(limit_boundary))
            current_bottommost = first_partially_rendered.client_bottom - self.client_top
            content_boundary.top = current_bottommost

        # rendering the things in the middle
        for child in self.children[full_render_range[0]:full_render_range[1]]:
            child.render(deepcopy(content_boundary))
            height_so_far = 
            content_boundary.top = height_so_far
             
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