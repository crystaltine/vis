from utils import parseattrs, cls, get_next_hoverable
from blessed import Terminal
from typing import List, Dict, Set, Any, TypedDict, Callable, Literal, TYPE_CHECKING
from pynput import keyboard
from key_event import KeyEvent
from time import sleep

if TYPE_CHECKING:
    from element import Element

class DocumentStyleProps(TypedDict):
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
    
    SUPPORTS_CHILDREN = True # obviously
    
    def __init__(self, style: DocumentStyleProps = {}, children: List["Element"] = [], quit_keys: List[str] = ["esc"]):
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

        self.hoverable_elements: Set["Element"] = set()
        """ Stores a set of pointers to elements that are HOVERABLE. """
        self.selectable_elements: Set["Element"] = set()
        """ Stores a set of pointers to elements that are SELECTABLE. """

        self.hovered: "Element | None" = None
        """ The currently hovered element. There can only be one at a time. """
        self.selected: "Element | None" = None
        """ The currently selected element. There can only be one at a time. 
        Also, unless we want to add a way for users to navigate the component tree
         while still having a selected element, this should equal `self.hoverable` if not None. """
        
        self.keyup_listeners: Set[Callable[[KeyEvent], Any]] = set()
        """ set of all KEYUP event callbacks. """
        self.keydown_listeners: Set[Callable[[KeyEvent], Any]] = set()
        """ set of all KEYDOWN event callbacks. """

        self.element_keyup_listeners: Dict["Element", Set[Callable[[KeyEvent], Any]]] = {}
        """ KEYUP event handlers registered by elements such as Input and Button """
        self.element_keydown_listeners: Dict["Element", Set[Callable[[KeyEvent], Any]]] = {}
        """ KEYDOWN event handlers registered by elements such as Input and Button """

        parseattrs(self, style, DocumentStyleProps.DEFAULT)
        
        self.client_left = 0
        self.client_top = 0
        self.client_right = self.term.width
        self.client_bottom = self.term.height
        
    def mount(self) -> None:
        """
        Mounts the document, renders all children, begins the app loop.
        """
        cls()
        
        self.render()

        with self.term.cbreak(), self.term.hidden_cursor():
            self.listener_thread = self._get_key_listener()
            self.listener_thread.start()
            self.listener_thread.join()
            
    def render(self) -> None:
        """
        Renders the document (no bg color yet lol) and all its children.
        """
        cls()
        for child in self.children:
            child.render(self.client_left, self.client_top, self.client_right, self.client_bottom)
            
    def add_child(self, child: "Element", index: int = None) -> None:
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
            
    def get_element_by_id(self, id: str) -> "Element | None":
        """
        Returns the element with the specified id. Returns None if no such element exists.
        """
        return self.id_map.get(id, None)

    def _get_key_listener(self) -> keyboard.Listener:
        """
        Returns a `Listener` thread for key presses. Run .start() on the returned object to start listening.
        """

        def _builtin_keydown_handler(ev: "KeyEvent"):
            """
            General functions built-in to the document, 
            such as exiting the program when quit keys are pressed,
            or selecting elements when arrow keys or tab is pressed.
            """
            if ev.key in self.quit_keys: self._quit()

            # select elements if tab, or arrow keys are pressed.
            # if the currently selected element has its own arrow-key/tab functionality,
            # then the event SHOULD be canceled by now and this shouldnt run.
            # but if we are here, we should find the next element to hover.
            if ev.key in ['up', 'down', 'left', 'right', 'tab']:
                self.hovered = get_next_hoverable(self.hoverable_elements, self.hovered, ev.key)
            elif ev.key == 'enter' and self.hovered and self.hovered.style.get("selectable"):
                self.selected = self.hovered
        
        def _builtin_keyup_handler(ev: "KeyEvent"):
            """
            General functions built-in to the document, 
            such as exiting the program when quit keys are pressed,
            or selecting elements when arrow keys or tab is pressed.
            """
            pass # nothing to do here yet

        def on_press(key: keyboard.Key | keyboard.KeyCode):
            
            KeyEvent.update_modifiers(key, "keydown")
            ev = KeyEvent.create_from(key)
                
            # run all keydown listeners for this key
            for listener in self.keydown_listeners:
                if ev.canceled: return
                listener(ev)

            # if ev was canceled, we would have returned already
            # run general document event handler last
            _builtin_keydown_handler(ev)

        def on_release(key: keyboard.Key | keyboard.KeyCode):
            
            KeyEvent.update_modifiers(key, "keyup")
            ev = KeyEvent.create_from(key)
            
            # run all keydown listeners for this key
            for listener in self.keyup_listeners:
                if ev.canceled: return
                listener(ev)

            # if ev was canceled, we would have returned already
            # run general document event handler last
            _builtin_keyup_handler(ev)
                
        return keyboard.Listener(on_press=on_press, on_release=on_release)
    
    def _quit(self):
        """
        Quits the app.
        """
        cls()
        print("\033[0m")
        sleep(0.5)
        exit()
    
    def add_event_listener(self, event: Literal["keydown", "keyup"], callback: Callable[[KeyEvent], None]):
        """
        Adds a document-wide event listener for either keydown or keyup. 
        Can have multiple listeners for the same key event.
        """
        
        listener_bank = self.keydown_listeners if event == "keydown" else self.keyup_listeners
        listener_bank.add(callback)
        
    def remove_event_listener(self, event: Literal["keydown", "keyup"], callback: Callable):
        """
        Removes an event listener for a specific key event. 
        Must pass the exact same function that was added, meaning references must be the same.
        
        Raises a KeyError if the callback is not found.
        """
        listener_bank = self.keydown_listeners if event == "keydown" else self.keyup_listeners
        listener_bank.remove(callback)
        
    def remove_all_event_listeners(self, event: Literal["keydown", "keyup"]):
        """
        Removes all event listeners for a specific key event.
        """
        listener_bank = self.keydown_listeners if event == "keydown" else self.keyup_listeners
        listener_bank.clear()
