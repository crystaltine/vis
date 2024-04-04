from utils import parseattrs, cls, get_next_hoverable
from blessed import Terminal
from typing import List, Dict, Set, Any, TypedDict, Callable, Literal, TYPE_CHECKING
from pynput import keyboard
from key_event import KeyEvent
from logger import Logger
from time import sleep
import traceback
from button import Button
from os import _exit

if TYPE_CHECKING:
    from element import Element

class Document:
    """
    A wrapper over a `blessed.Terminal` object. Represents the root of the component tree, 
    basically just one giant HTML-like div containing all the elements on the screen.
    """

    class StyleProps(TypedDict):
        """
        A schema of style options for the document.
        """
        bg_color: str | tuple
    
    SUPPORTS_CHILDREN = True # obviously
    DEFAULT_STYLE: "StyleProps" = {
        "bg_color": "#ffffff"
    }
    
    def __init__(self, style: "StyleProps" = {}, children: List["Element"] = [], quit_keys: List[str] = ["esc"]):
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
        self._exited = False

        self.hoverable_elements: Set["Element"] = set()
        """ Stores a set of pointers to elements that are HOVERABLE. """
        self.selectable_elements: Set["Element"] = set()
        """ Stores a set of pointers to elements that are SELECTABLE. """

        self.hovered: "Element | None" = None
        """ The currently hovered element. There can only be one at a time. Must be the same as `self.active` if it is not None."""
        self.active: "Element | None" = None
        """ The currently active element. There can only be one at a time. 
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

        parseattrs(self, style, Document.DEFAULT_STYLE)
        
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

        with self.term.cbreak():
            self.listener_thread = self._get_key_listener()
            self.listener_thread.start()

    def render(self) -> None:
        """
        Renders the document (no bg color yet lol) and all its children.
        """
        try:
            cls()
            for child in self.children:
                Logger.log(f"document.render: rendering child with client edges {self.client_left=} {self.client_top=} {self.client_right=} {self.client_bottom=}")
                child.render(self.client_left, self.client_top, self.client_right, self.client_bottom)
                    
        except Exception as e:
            Logger.log(f"ERROR in document.render: {traceback.format_exc()}")
            self.quit_app(f"ERROR in document.render: {traceback.format_exc()}")
            
    def add_child(self, child: "Element", index: int = None) -> None:
        """
        Adds a child div at the specified index, which means where on the component tree it will be placed.
        If index is None, it will be added to the end of the list of children.
        """
        Logger.log(f"document: adding child {child}, id={child.id}")
        
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
            
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
            
            Does not deal with keydown listeners added through `document.add_event_listener`.
            
            These built-in handlers will NOT run if a currently selected element 
            also handles these keys.
            """
            
            try:
                # exiting program
                if ev.key in self.quit_keys: 
                    self.quit_app("hit quit key")
                
                elif ev.key == 'enter' and self.hovered and self.hovered.style.get("selectable"):
                    if self.active is not None: 
                        self.active.render()
                    self.active = self.hovered
                    self.active.render()
            
            except:
                Logger.log(f"ERROR in document._builtin_keydown_handler: {traceback.format_exc()}")
                self.quit_app(f"ERROR in document._builtin_keydown_handler: {traceback.format_exc()}")
        
        def _builtin_keyup_handler(ev: "KeyEvent"):
            """
            General functions built-in to the document, 
            such as exiting the program when quit keys are pressed,
            or selecting elements when arrow keys or tab is pressed.
            """
            pass
            try:
                # run the currently selected listeners IF it exists
                if (handlers := self.element_keyup_listeners.get(self.active)) is not None:
                    [func(ev) for func in handlers]
                    
            except Exception as e:
                Logger.log(f"ERROR in document._builtin_keyup_handler: {traceback.format_exc()}")
                self.quit_app(f"ERROR in document._builtin_keyup_handler: {traceback.format_exc()}")

        def on_press(key: keyboard.Key | keyboard.KeyCode):
            
            # creating keyevent obj
            KeyEvent.update_modifiers(key, "keydown")
            ev = KeyEvent.create_from(key)
            
            # tab and shift+tab are the master keys. If they are pressed, we always 
            # navigate around the component tree.
            if ev.key == 'tab':
                # TODO - have to handle shift+tab
                # technically we care if shift is being held.
                # for now, just deselect currently active, and move hover
                # to a random element in the document.
                
                temp = self.active
                self.active = None # move to next element, so get rid of active
                if temp is not None:
                    temp.render() # rerender to get rid of the active state (such as different bg)
                
                # set hovered to the new hovered element
                # as a precondition, hovered should have been self.active. We dont need to rerender it to get rid of the hover state.
                temp = self.hovered                
                self.hovered = get_next_hoverable(self.hoverable_elements, self.hovered, ev)
                self.hovered.render()
                if temp is not None:
                    temp.render()
                
                return # dont run the rest of the code
            
            elif ev.key == 'enter':
                if isinstance(btn:=self.hovered, Button):
                    # select the button and run its on_pressed ONLY if it wasnt active before (no holding by default) <-TODO add opt to change this later?
                    if self.active is not btn:
                        self.active = btn
                        btn.render()
                        btn.on_pressed()
            
            #  always run selected element's keydown listeners, and any custom document-wide listeners\
            if self.active is not None:
                if (handlers := self.element_keydown_listeners.get(self.active)) is not None:
                    [func(ev) for func in handlers]

            # run all defined keydown listeners, breaking if any of them cancel the event
            for listener in self.keydown_listeners:
                if ev.canceled: return
                listener(ev)
                
            if self.active is None:
                # only run builtin if we arent currently handling the key in the selected element
                # this also doesnt work if some defined handler canceled the event
                _builtin_keydown_handler(ev)

        def on_release(key: keyboard.Key | keyboard.KeyCode):
            
            KeyEvent.update_modifiers(key, "keyup")
            ev = KeyEvent.create_from(key)
            
            if isinstance(btn:=self.hovered, Button):
                if ev.key == 'enter':
                    # enter was released, deselect the button
                    self.active = None
                    btn.render()
            
            if self.active is not None:
                if (handlers := self.element_keyup_listeners.get(self.active)) is not None:
                    [func(ev) for func in handlers]
            
            for listener in self.keyup_listeners:
                if ev.canceled: return
                listener(ev)

            if self.active is None:
                _builtin_keyup_handler(ev)
                
        return keyboard.Listener(on_press=on_press, on_release=on_release)
    
    def quit_app(self, exit_msg = None):
        """
        Quits the app. Also writes the log to a file.
        Prints an exit message if provided.
        """
        cls()
        print(self.term.normal)
        Logger.write()
        if exit_msg:
            print(exit_msg)
        _exit(0)
    
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
