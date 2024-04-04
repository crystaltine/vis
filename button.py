from element import Element
from utils import fcode, convert_to_chars
from typing import TYPE_CHECKING, List, Unpack, Callable, Any
from globalvars import Globals
from logger import Logger

if TYPE_CHECKING:
    from key_event import KeyEvent

class Button(Element):
    """
    Basically a div but is selectable, takes a "pressed" handler,
    and generally does typical button behavior.
    """
    
    class Attributes(Element.Attributes):
        id: str | None
        class_str: str | None
        style_str: str | None
        children: List[Element]
        on_pressed: Callable[[], Any]
        #disabled: bool
    
    class StyleProps(Element.StyleProps):
        """ A schema of style options for buttons. """
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
        hovered_bg_color: str | tuple
        pressed_bg_color: str | tuple
    
    SUPPORTS_CHILDREN = True
    DEFAULT_STYLE: "StyleProps" = {
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
        "color": (255, 255, 255),
        "hovered_color": (255, 255, 255),
        "pressed_color": (255, 255, 255),
        "bg_color": "#1285dd",
        "hovered_bg_color": "#075dd4",
        "pressed_bg_color": "#0050be",
    }

    def __init__(self, **attrs: Unpack["Attributes"]):
        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        
        # assert that ONE of left/right and ONE of top/bottom is provided
        assert (self.style.get("left") is not None or self.style.get("right") is not None), "[Button]: At least one of left or right must not be None."
        assert (self.style.get("top") is not None or self.style.get("bottom") is not None), "[Button]: At least one of top or bottom must not be None."

        self.on_pressed: Callable[[], Any] = attrs.get("on_pressed", lambda: None)
        """ Event handler to run when the button is pressed (enter is pressed down while it is hovered). Modifiable. """
        
        self.children: List["Element"] = attrs.get("children", [])
        self._bg_fcode = fcode(background=self.style.get("bg_color")) if self.style.get("bg_color") != "transparent" else None

        # NEW: this is all handled within the document event handler as a special case.
        # register this element's event handler with the document's special handlers
        #Globals.__vis_document__.element_keydown_listeners[self] = set([_event_handler])
        Globals.__vis_document__.selectable_elements.add(self)
        Globals.__vis_document__.hoverable_elements.add(self)
    
    def render(self, container_left: int = None, container_top: int = None, container_right: int = None, container_bottom: int = None):

        Logger.log(f"<BEGIN BUTTON render func>")
        #Logger.log(f"Button render params: {container_left=} {container_top=} {container_right=} {container_bottom=}")
        container_left, container_top, container_right, container_bottom = self.get_true_container_edges(container_left, container_top, container_right, container_bottom)
        
        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        # Calculating client edges #############################################   
        
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
        
        #########################################################################
        
        #Logger.log(f"Button (id={self.id}) given top: {self.style.get('top')}, bottom: {self.style.get('bottom')}, height: {self.style.get('height')}, calced client_top={self.client_top}, client_bottom={self.client_bottom}, client_height={self.client_height}")
        #Logger.log(f"^ container top: {container_top}, bottom: {container_bottom}, height: {container_height}")
        
        # ditch everything else if invisible.
        if not self.style.get("visible"): return
        
        # draw the rectangle IF it is not transparent.
        bg_color_to_use = self.style.get(
            "bg_color" if (not Globals.is_active(self)) and (not Globals.is_hovered(self))
            else "hovered_bg_color" if Globals.is_hovered(self) and not Globals.is_active(self)
            else "pressed_bg_color"
        )
        if bg_color_to_use != "transparent":   
            active_bg_fcode = fcode(background=bg_color_to_use)
            with Globals.__vis_document__.term.hidden_cursor():
                for i in range(self.client_top, self.client_bottom):
                    print(Globals.__vis_document__.term.move_xy(self.client_left, i) + active_bg_fcode + " " * self.client_width, end="")
                        
        # render children
        for child in self.children:
            
            if self is child: continue # ??? - for some reason using this func adds a self pointer to its own children. try fixing later
            
            general_padding = convert_to_chars(container_width, self.style.get("padding")) if self.style.get("padding") is not None else 0
            child.render(
                self.client_left + convert_to_chars(container_width, self.style.get("padding_left")) or general_padding,
                self.client_top + convert_to_chars(container_height, self.style.get("padding_top")) or general_padding,
                self.client_right - convert_to_chars(container_width, self.style.get("padding_right")) or general_padding,
                self.client_bottom - convert_to_chars(container_height, self.style.get("padding_bottom")) or general_padding
            )
             
    def add_child(self, child: "Element", index: int = None):
        """
        Adds a child at the specified index, which means where on this element's component tree it will be placed.
        If index is None, it will be added to the end of the list of children.
        
        @TODO - for some reason, this leads to a recursion error because objects get added all over the document. IDK why!!
        (probably pointer/inheritance issue)
        """
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
            
        #Logger.log(f"Added child to {self}: {child}")