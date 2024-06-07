from utils import parseattrs, cls, get_next_hoverable
from blessed import Terminal
from typing import List, Dict, Set, Any, TypedDict, Callable, Literal, TYPE_CHECKING
from threading import Thread
from key_event import KeyEvent2
from logger import Logger
from boundary import Boundary
import traceback
from button import Button
from os import _exit
from time import time

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke
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
    
    def __init__(self, style: "StyleProps" = {}, children: List["Element"] = [], quit_keys: List[str] = ["q", "\x1b"]):
        """
        `style`: See `DocumentStyle`. If a value is not provided, it will be set to the default.
        `children`: A list of elements to be rendered in the document.
        `quit_keys`: A list of keys that, when pressed, will exit the app.
        """

        Logger.log(f"creating new document object")

        self.stopped = False
        
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
        
        self.key_listeners: Set[Callable[[KeyEvent2], Any]] = set()
        """ set of all KEYDOWN event callbacks. """

        self.element_key_listeners: Dict["Element", Set[Callable[[KeyEvent2], Any]]] = {}
        """ KEYDOWN event handlers registered by elements such as Input and Button """

        self.listener_thread = None
        self.listener_kill_flag = False
        """ tells the listener thread to stop listening, if true. """

        parseattrs(self, style, Document.DEFAULT_STYLE)
        
        self.client_left = 0
        self.client_top = 0
        self.client_right = self.term.width
        self.client_bottom = self.term.height
        
    def mount(self) -> None:
        """
        Mounts the document, renders all children, begins the app loop.
        """

        #cls()
        #Logger.log(f"t={time()}: doc.mount is about to print HI call self.render")
        #print(f"HI")
        
        self.render()

        self.listener_thread = self._get_key_listener()
        self.listener_thread.start()

    def render(self) -> None:
        """
        Renders the document (no bg color yet lol) and all its children.
        """
        try:
            #cls()
            with self.term.hidden_cursor():
                for child in self.children:
                    Logger.log(f"document.render: rendering child with client edges {self.client_left=} {self.client_top=} {self.client_right=} {self.client_bottom=}")
                    child.render(Boundary(self.client_left, self.client_top, self.client_right, self.client_bottom))
                        
        except Exception as e:
            Logger.log(f"ERROR in document.render: {traceback.format_exc()}")
            self.quit_app(f"ERROR in document.render: {traceback.format_exc()}")

    def derender(self) -> None:
        """
        Removes all traces of this document (in case of switching screens)
        but does not terminate the main thread.
        """
        cls()
        print(self.term.normal)
        self.listener_kill_flag = True
            
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

    def _get_key_listener(self) -> Thread:
        """
        Returns a `Listener` thread for key presses. Run .start() on the returned object to start listening.
        """

        def _builtin_key_handler(ev: "KeyEvent2"):
            """
            General functions built-in to the document, 
            such as exiting the program when quit keys are pressed,
            or selecting elements when arrow keys or tab is pressed.
            
            Does not deal with key listeners added through `document.add_event_listener`.
            
            These built-in handlers will NOT run if a currently selected element 
            also handles these keys.
            """
            
            try:
                # exiting program
                if ev.key in self.quit_keys: 
                    Logger.log(f"a quit key was pressed: {[ev.key]}")
                    self.quit_app()
                
                elif ev.name == 'KEY_ENTER' and self.hovered and self.hovered.style.get("selectable"):
                    if self.active is not None: 
                        self.active.render()
                    self.active.on_deselect() if hasattr(self.active, 'on_deselect') else None # first, deselect the currently active element
                    self.active = self.hovered # then, set active to new hovered element
                    self.active.on_select() if hasattr(self.active, 'on_select') else None
                    self.active.render()
            
            except:
                Logger.log(f"ERROR in document._builtin_keydown_handler: {traceback.format_exc()}")
                self.quit_app(f"ERROR in document._builtin_keydown_handler: {traceback.format_exc()}")

        def on_press(key: "Keystroke"):
            Logger.log(f"on_press now running with key name,key={key.name},{key}")
            # check if key came from the current window
            ev = KeyEvent2.create_from(key)
            #Logger.log_on_screen(f"on_press created {ev}")
            
            # tab and shift+tab are the master keys. If they are pressed, we always 
            # navigate around the component tree.
            if ev.name == 'KEY_TAB':
                # TODO - have to handle shift+tab
                # technically we care if shift is being held.
                # for now, just deselect currently active, and move hover
                # to a random element in the document.
                
                temp = self.active
                temp.on_deselect() if hasattr(temp, 'on_deselect') else None
                self.active = None # move to next element, so get rid of active
                if temp is not None:
                    temp.render() # rerender to get rid of the active state (such as different bg)
                
                # set hovered to the new hovered element
                # as a precondition, hovered should have been self.active. We dont need to rerender it to get rid of the hover state.
                temp = self.hovered  
                temp.on_dehover() if hasattr(temp, 'on_dehover') else None              
                self.hovered = get_next_hoverable(self.hoverable_elements, self.hovered, ev)
                self.hovered.on_hover() if hasattr(self.hovered, 'on_hover') else None
                self.hovered.render()
                if temp is not None:
                    temp.render()
                
                return # dont run the rest of the code
            
            elif ev.name == 'KEY_ENTER':
                if isinstance(btn:=self.hovered, Button):
                    # select the button and run its on_pressed ONLY if it wasnt active before (no holding by default) <-TODO add opt to change this later?
                    if self.active is not btn:
                        if self.active is not None:
                            self.active.on_deselect() if hasattr(self.active, 'on_deselect') else None
                        self.active = btn
                        btn.render()
                        btn.on_pressed()
            
            #  always run selected element's keydown listeners, and any custom document-wide listeners\
            if self.active is not None:
                if (handlers := self.element_key_listeners.get(self.active)) is not None:
                    [func(ev) for func in handlers]

            # run all defined keydown listeners, breaking if any of them cancel the event
            for listener in self.key_listeners:
                if ev.canceled: return
                listener(ev)
                
            if self.active is None:
                # only run builtin if we arent currently handling the key in the selected element
                # this also doesnt work if some defined handler canceled the event
                _builtin_key_handler(ev)
        
        def listener_loop():
            try:
                while True:
                    with self.term.cbreak():
                        val = self.term.inkey(0.01)
                        Logger.log(f"document.listener_loop: got key {val}")
                        
                        # if the listener thread is killed, or the document is stopped, break the loop
                        if self.stopped or self.listener_kill_flag: break
                        
                        # otherwise just keep listening
                        if not val: continue
                        
                        on_press(val)
            except:
                Logger.log(f"ERROR in document.listener_loop: {traceback.format_exc()}")
                self.quit_app(f"\x1b[33mERROR in Document Event Listener: \x1b[31m{traceback.format_exc()}\x1b[0m")
                
        return Thread(target=listener_loop)
    
    def quit_app(self, exit_msg = None):
        """
        Quits the app. Also writes the log to a file.
        Prints an exit message if provided.
        """
        self.stopped = True
        cls()
        print(self.term.normal)
        
        Logger.write()
        
        if exit_msg:
            print(exit_msg)
        _exit(0)
    
    def add_event_listener(self, callback: Callable[[KeyEvent2], None]):
        """
        Adds a document-wide event listener for keypresses. Multiple listeners are supported.
        """
        
        self.key_listeners.add(callback)
        
    def remove_event_listener(self, callback: Callable):
        """
        Removes an event listener for a specific key event. 
        Must pass the exact same function that was added, meaning references must be the same.
        
        Raises a KeyError if the callback is not found.
        """
        self.key_listeners.remove(callback)
        
    def remove_all_event_listeners(self):
        """
        Removes all event listeners for a specific key event.
        """
        self.key_listeners.clear()
