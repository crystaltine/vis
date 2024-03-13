from common import StylePropDict, parseattrs, cls
from blessed import Terminal
from typing import List, Dict, Set, Callable, Literal, TYPE_CHECKING
from pynput import keyboard

if TYPE_CHECKING:
    from common import Element, KeyEvent

class DocumentStyleProps(StylePropDict):
    """
    A schema of style options for the document.
    """
    bg_color: str | tuple
    
    DEFAULT: "DocumentStyleProps" = {
        "bg_color": "#ffffff"
    }

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

        self.selected: "Element" = None
        
        self.keyup_listeners: Set[Callable[[KeyEvent], None]] = set()
        """ set of all KEYUP event callbacks. """
        self.keydown_listeners: Set[Callable[[KeyEvent], None]] = set()
        """ set of all KEYDOWN event callbacks. """

        self.element_keyup_listeners: Dict["Element", Set[Callable[[KeyEvent], None]]] = {}
        """ KEYUP event handlers registered by elements such as Input and Button """
        self.element_keydown_listeners: Dict["Element", Set(Callable[[KeyEvent], None])] = {}
        """ KEYDOWN event handlers registered by elements such as Input and Button """

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

            # create KeyEvent object
            key_char = getattr(key, "char", default="")
            ev = KeyEvent()
                
            # run all keydown listeners for this key
            [listener() for listener in self.keydown_listeners.get(key, set())]
            
        def on_release(key):
            #print(f"onrelease: key: {key}")
            # run all keyup listeners for this key
            [listener() for listener in self.keyup_listeners.get(key, set())]
                
        return keyboard.Listener(on_press=on_press, on_release=on_release)
    
    def add_event_listener(self, type: Literal["keydown", "keyup"], callback: Callable[[KeyEvent], None]):
        """
        Adds a document-wide event listener for either keydown or keyup. 
        Can have multiple listeners for the same key event.
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
