from typing import List, TypedDict, Literal, Dict, Callable, Set
from utils import fcode, cls
from blessed import Terminal
from abc import ABC, abstractmethod
from pynput import keyboard
from logger import Logger

def parseattrs(object, provided_opts: dict | None, default: dict):
    """
    Looks at `provided_opts` and, for every key in `provided_opts` that also appears in `default`,
    sets the associated value as a field on `object`, using the value from `default` if not provided.
    """
    
    if provided_opts is None:
        provided_opts = {}
    
    for key in default:
        
        # print(f"\x1b[34mparseattr: setting {key} to {provided_opts.get(key, default[key])} on {object}\x1b[0m")
        setattr(object, key, provided_opts.get(key, default[key]))
 
def calculate_dim(container_dim: int, dimvalue: int | str) -> int:
    """
    Returns the actual value of the dimension (in characters) based on the container size.
    
    `dimvalue` must be a string ending in 'ch' or '%'.
    
    `container_dim`: the size of the container in the dimension we're calculating.
    
    examples:
    - `calculate_dim(120, '50%') -> 60`
    - `calculate_dim(120, '324234ch') -> 324234` (why would you do this)
    """
    
    # if int, assume as raw character value
    if isinstance(dimvalue, int): return dimvalue
    
    if dimvalue[-2:] == 'ch':
        return int(dimvalue[:-2])
    elif dimvalue[-1] == '%':
        return round(container_dim * int(dimvalue[:-1]) / 100)
    else:
        raise ValueError(f"Invalid dimvalue: {dimvalue}. Must end in 'ch' or '%'.")    

class StylePropDict(TypedDict):
    
    DEFAULT: "StylePropDict"
    """ A dict that contains the default values for the style options. """

class TextStyleProps(StylePropDict):
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
    
    DEFAULT: "TextStyleProps" = {
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
    }
        
class DivStyleProps(StylePropDict):
    """
    A schema of style options for divs.
    """
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
    
    DEFAULT: "DivStyleProps" = {
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
        "bg_color": (255, 255, 255) # can be hex code, rgb tuple, or 'transparent'
    }

class DocumentStyleProps(StylePropDict):
    """
    A schema of style options for the document.
    """
    bg_color: str | tuple
    
    DEFAULT: "DocumentStyleProps" = {
        "bg_color": "#ffffff"
    }

class Element:
    """
    An abstract class representing a generic element in the component tree.
    """
    
    document: "Document"
    """ A reference to the root document object the element is rendered on. This is for thing like event handler registration. """
    
    id: str | None
    """ An identifier for the element, which can be used to reference it (using `Document.get_element_by_id`) """
    
    client_left: int | None
    """ The absolute x-position of the left of the element on the screen. 
    0 is the left edge of the screen. is `None` if element hasn't been rendered yet. """
    
    client_top: int | None
    """ The absolute y-position of top the of the element on the screen. 
    0 is the top edge of the screen. is `None` if element hasn't been rendered yet."""
    
    client_right: int | None
    """ 1 + the absolute x-position of the right of the element on the screen. 
    0 is still the left edge of the screen. (notice the +1). is `None` if element hasn't been rendered yet. """
    
    client_bottom: int | None
    """ 1 + the absolute y-position of the bottom of the element on the screen. 
    0 is still the top edge of the screen. (notice the +1). is `None` if element hasn't been rendered yet. """

    def __init__(self, id: str | None, style: dict | None, style_dict: StylePropDict,  *args, **kwargs):
        
        parseattrs(self, style, style_dict.DEFAULT)
        
        self.document = globals()["__vis_document__"]
        self.id = id
        self.client_left = None
        self.client_top = None
        self.client_right = None
        self.client_bottom = None

    @abstractmethod
    def render(self, container_left: int, container_top: int, container_right: int, container_bottom: int) -> None:
        """ Renders the element to its container at the specified position, given the positions of the container. """
        ...

class Document:
    """
    A wrapper over a `blessed.Terminal` object. Represents the root of the component tree, 
    basically just one giant HTML-like div containing all the elements on the screen.
    """
    def __init__(self, style: DocumentStyleProps = {}, children: List["Element"] = [], quit_keys: List[keyboard.Key] = [keyboard.Key.esc]):
        """
        `style`: See `DocumentStyle`. If a value is not provided, it will be set to the default.
        `children`: A list of elements to be rendered in the document.
        `quit_keys`: A list of keys that, when pressed, will exit the app.
        """
        
        self.children = children
        self.id_map: Dict[str, "Element"] = {} # Dict[str, List["Element"]] = {} <- if we wanna allow non-unique ids
        """ Stores references to elements that were given an id. """
        self.term = Terminal()
        
        self.quit_keys = quit_keys
        
        self.keyup_listeners: Dict[str, Set[Callable]] = {}
        """ Maps KEYUP events to callbacks. """
        self.keydown_listeners: Dict[str, Set[Callable]] = {}
        """ Maps KEYDOWN events to callbacks. """
        
        parseattrs(self, style, DocumentStyleProps.DEFAULT)
        
        self.client_left = 0
        self.client_top = 0
        self.client_right = self.term.width
        self.client_bottom = self.term.height
        
    def mount(self):
        """
        Mounts the document, renders all children, begins the app loop.
        """
        cls()
        
        self.render()

        with self.term.cbreak():
            self.listener_thread = self._get_key_listener()
            self.listener_thread.start()
            
    def render(self):
        """
        Renders all children.
        """
        cls()
        for child in self.children:
            child.render(self.client_left, self.client_top, self.client_right, self.client_bottom)
            
    def add_child(self, child: "Element", index: int = None):
        """
        Adds a child div at the specified index, which means where on the component tree it will be placed.
        If index is None, it will be added to the end of the list of children.
        """
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
            
        # if the child has an id, add it to the id_map
        if child.id:
            if child.id in self.id_map:
                raise ValueError(f"Cannot add element to Document: an element with id '{child.id}' already exists.")
            
            self.id_map[child.id] = child
            
    def get_element_by_id(self, id: str) -> Element | None:
        """
        Returns the element with the specified id. Returns None if no such element exists.
        """
        return self.id_map.get(id, None)

    def _get_key_listener(self):
        """
        Returns a `Listener` thread for key presses. Run .start() on the returned object to start listening.
        """
        def on_press(key):
            if key in self.quit_keys:
                cls()
                print("\x1b[0m", end="") # reset formatting
                exit()
                
            # run all keydown listeners for this key
            [listener() for listener in self.keydown_listeners.get(key, set())]
            
        def on_release(key):
            #print(f"onrelease: key: {key}")
            # run all keyup listeners for this key
            [listener() for listener in self.keyup_listeners.get(key, set())]
                
        return keyboard.Listener(on_press=on_press, on_release=on_release)
    
    def add_event_listener(self, keyname: str, type: Literal["keydown", "keyup"], callback: Callable):
        """
        Adds an event listener for a specific key event. Can have multiple listeners for the same key event.
        """
        
        listener_bank = self.keydown_listeners if type == "keydown" else self.keyup_listeners
        
        if keyname not in listener_bank:
            listener_bank[keyname] = set()
        listener_bank[keyname].add(callback)
        
    def remove_event_listener(self, keyname: str, type: Literal["keydown", "keyup"], callback: Callable):
        """
        Removes an event listener for a specific key event. 
        Must pass the exact same function that was added, meaning references must be the same.
        
        Raises a KeyError if the callback is not found.
        """
        listener_bank = self.keydown_listeners if type == "keydown" else self.keyup_listeners
        
        listener_bank[keyname].remove(callback)
        
    def remove_all_event_listeners(self, keyname: str, type: Literal["keydown", "keyup"]):
        """
        Removes all event listeners for a specific key event.
        """
        listener_bank = self.keydown_listeners if type == "keydown" else self.keyup_listeners
        
        listener_bank[keyname].clear()

class Div(Element):
    """
    A general div class with customizable styling options.
    Can use either percents or characters to set size.
    """

    def __init__(self, style: DivStyleProps = {}, id: str = None, children: List["Element"] = []):
        """
        `style`: See `DivStyle`. If a value is not provided, it will be set to the default.
        
        Note: For options that conflict, such as "top"/"bottom" and "height", the ones listed higher
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
        
        super().__init__(id, style, DivStyleProps)
        
        # assert that ONE of left/right and ONE of top/bottom is provided
        assert (self.left is not None or self.right is not None), "[Div]: At least one of left or right must not be None."
        assert (self.top is not None or self.bottom is not None), "[Div]: At least one of top or bottom must not be None."
        
        self.children = children
        self.bg_fcode = fcode(background=self.bg_color) if self.bg_color != "transparent" else None
        #Logger.log(f"{self}'s children on init: {self.children}")
    
    def render(self, container_left: int, container_top: int, container_right: int, container_bottom: int):
        """
        Draws the rectangle to the container based on current screen size (for any percents)
        """
        
        #Logger.log(f"{self}'s children on render: {self.children}")
        
        container_left = container_left if self.position == "relative" else 0
        container_top = container_top if self.position == "relative" else 0
        container_right = container_right if self.position == "relative" else __vis_document__.term.width
        container_bottom = container_bottom if self.position == "relative" else __vis_document__.term.height
        
        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        self.client_top = container_top + (calculate_dim(container_height, self.top) if self.top 
            else calculate_dim(container_height, self.bottom) - calculate_dim(container_height, self.height))
        
        self.client_bottom = container_top + (calculate_dim(container_height, self.bottom) if self.bottom
            else calculate_dim(container_height, self.top) + calculate_dim(container_height, self.height))
        
        self.client_height = self.client_bottom - self.client_top
        
        self.client_left = container_left + (calculate_dim(container_width, self.left) if self.left
            else calculate_dim(container_width, self.right) - calculate_dim(container_width, self.width))
        
        self.client_right = container_left + (calculate_dim(container_width, self.right) if self.right
            else calculate_dim(container_width, self.left) + calculate_dim(container_width, self.width))
        
        self.client_width = self.client_right - self.client_left
        
        if not self.visible: return
        
        # draw the rectangle IF it is not transparent.
        if self.bg_fcode:
            for i in range(self.client_top, self.client_bottom):
                with __vis_document__.term.hidden_cursor():
                    print(__vis_document__.term.move_xy(self.client_left, i) + self.bg_fcode + " " * self.client_width, end="")
                    
        # render children
        for child in self.children:
            
            if self is child: continue
            
            child.render(
                self.client_left + self.padding_left or self.padding or 0,
                self.client_top + self.padding_top or self.padding or 0,
                self.client_right - self.padding_right or self.padding or 0,
                self.client_bottom - self.padding_bottom or self.padding or 0
            )
             
    def add_child(self, child: "Element", index: int = None):
        """
        Adds a child div at the specified index, which means where on the component tree it will be placed.
        If index is None, it will be added to the end of the list of children.
        
        @TODO - for some reason, this leads to a recursion error because objects get added all over the document. IDK why!!
        """
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
            
        #Logger.log(f"Added child to {self}: {child}")
            
class Text(Element):
    """
    Represents text that can be placed inside any element.
    """
    def __init__(self, text: str = "", style: TextStyleProps = {}, id: str = None):
        
        super().__init__(id, style, TextStyleProps)
        self.text = text
        
        # assert that not both left and right are None
        assert (self.left is not None or self.right is not None), "[Text]: At least one of left or right must not be None."
        
    def render(self, container_left: int, container_top: int, container_right: int, container_bottom: int):
        """
        Renders the text to its container at the specified position, given the positions of the container.
        """
        
        container_left = container_left if self.position == "relative" else 0
        container_top = container_top if self.position == "relative" else 0
        container_right = container_right if self.position == "relative" else __vis_document__.term.width
        container_bottom = container_bottom if self.position == "relative" else __vis_document__.term.height
        
        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        text_len = len(self.text)
        text_left_pos = 0
        
        # calculate text left position
        if self.left is not None:
            text_left_pos = container_left + calculate_dim(container_width, self.left) - (
                0 if self.text_align == "left" else
                text_len // 2 if self.text_align == "center" else
                text_len
            )
        elif self.right is not None:
            text_left_pos = container_left + calculate_dim(container_width, self.right) - text_len + (
                0 if self.text_align == "left" else
                text_len // 2 if self.text_align == "center" else
                text_len
            )
            
        # set client_... attributes just for info
        self.client_left = text_left_pos
        self.client_right = self.client_left + text_len
        self.client_top = container_top + calculate_dim(container_height, self.y)
        self.client_bottom = self.client_top + 1
        
        if not self.visible: return
            
        style_string = " ".join([
            "bold" if self.bold else "",
            "italic" if self.italic else "",
            "underline" if self.underline else ""
        ])
        
        with __vis_document__.term.hidden_cursor():
            print(__vis_document__.term.move_xy(self.client_left, self.client_top) + fcode(self.color, background=self.bg_color, style=style_string) + self.text, end="")

global __vis_document__ 
__vis_document__ = Document()
__vis_document__.add_child(Div(
    style={
        "left": "0%", 
        "top": "0%", 
        "width": "100%", 
        "height": "100%", 
        "bg_color": "#2a2a37",
    },
    children=[
        Div(
            style={
                "left": "30%", 
                "top": "30%", 
                "width": "40%", 
                "height": "40%", 
                "bg_color": "#3d3d4f", 
            },
            children=[
                Div(
                    style={
                        "left": "10%", 
                        "top": "10%", 
                        "width": "80%", 
                        "height": "80%", 
                        "bg_color": "#4d4d66", 
                    },
                    children=[
                        Text(
                            text="CENTER JUSTIFIED TEXT!!!!!",
                            style={
                                "color": "aqua",
                                "bg_color": "black",
                                "left": "50%",
                                "y": "50%",
                                "text_align": "center",
                            }
                        ),
                        Text(
                            text="some more text but its right justified",
                            style={
                                "color": "yellow",
                                "bg_color": "red",
                                "italic": True,
                                "left": "90%",
                                "y": "20%",
                                "text_align": "right",
                            }
                        ),
                    ]
                )
            ]
        )
    ])
)

__vis_document__.mount()

__vis_document__.listener_thread.join() # remove if main thread is polling self.keys
Logger.write()