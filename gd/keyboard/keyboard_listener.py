from typing import Literal, Callable, Dict, List
import win32gui
from uuid import uuid4
import os
from pynput.keyboard import Listener, Key, KeyCode
from logger import Logger
from keyboard.key_event import KeyEvent

SpecialKey = Literal[
    'space', 'tab',
    'ctrl', 'ctrl_l', 'ctrl_r', 
    'alt', 'alt_l', 'alt_r', 'alt_gr',
    'shift', 'shift_l', 'shift_r',
    'cmd', 'cmd_l', 'cmd_r', 
    'up', 'down', 'left', 'right',
    'backspace', 'delete', 'insert', 
    'caps_lock', 'num_lock', 'scroll_lock',
    'enter', 
    'esc', 
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 
    'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24', 
    'home', 'end', 'page_down', 'page_up',
    'media_play_pause', 'media_volume_mute', 'media_volume_down', 'media_volume_up', 'media_previous', 'media_next', 
    'menu', # windows key (i think) or whatever is on mac 
    'pause', 
    'print_screen',
]
NormalKey = Literal[ 
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '-', '=', '[', ']', '\\', ';', "'", ',', '.', '/', '`',
]

class KeyboardListener:
    """ 
    static class to handle pynput keyboard stuff, which allows for detecting whether or not a key is held down (not just pressed) 
    
    List of all supported SPECIAL keys (obviously, letters/numbers/symbols are just represented by their own values), as of Jun 5 2024:
    ```
    [
        'space', 'tab',
        'ctrl', 'ctrl_l', 'ctrl_r', 
        'alt', 'alt_l', 'alt_r', 'alt_gr',
        'shift', 'shift_l', 'shift_r',
        'cmd', 'cmd_l', 'cmd_r', 
        'up', 'down', 'left', 'right',
        'backspace', 'delete', 'insert', 
        'caps_lock', 'num_lock', 'scroll_lock',
        'enter', 
        'esc', 
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 
        'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24', 
        'home', 'end', 'page_down', 'page_up',
        'media_play_pause', 'media_volume_mute', 'media_volume_down', 'media_volume_up', 'media_previous', 'media_next', 
        'menu', # windows key (i think) or whatever is on mac 
        'pause', 
        'print_screen',
    ]
    ```
    """
    
    listener = None
    """ The pynput Listener object represented by this class. Is None if not started. """
    window_name = uuid4().hex
    """ Starting the listener will set the terminal window name to this, exactly once per start(). Used to check if key events are from the current window."""
    keys: Dict[NormalKey | SpecialKey, bool] = {}
    """ A dict mapping every key name to a boolean indicating whether or not it is currently held down. """
    on_presses: List[Callable[[KeyEvent], None]] = []
    """ list of handlers for when a key is pressed down. All get run on event emit """
    on_releases: List[Callable[[KeyEvent], None]] = []
    """ list of handlers for when a key is released. All get run on event emit """
    
    def start():
        """ Starts a separate thread to start collecting keyboard info (updates `keys` dict continuously).
        
        If already started and not stopped, stops the current listener and starts a new one.
        
        Key events are only used if they are from the current window. 
        ### NOTE: This function will RENAME the current terminal window in order to detect key events from it.
        ### NOTE2: Only works on windows for now. """
        
        if KeyboardListener.listener is not None:
            KeyboardListener.stop()
        
        os.system(f"title {KeyboardListener.window_name}")
        
        def get_listener_func(event: Literal['keybown', 'keyup']) -> Callable[[Key | KeyCode], None]:
            def listener_inner(key: Key | KeyCode) -> None:               
                
                if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != KeyboardListener.window_name: return
                if key is None: return
                
                identifier = (
                    key.char if isinstance(key, KeyCode) else
                    " " if key.name == "space" else
                    key.name
                )

                KeyboardListener.keys[identifier] = event == "keydown"
                
                # run handlers
                KeyEvent.update_modifiers(key, event)
                ke = KeyEvent.create_from(key)
                
                if event == "keydown":
                    [func(ke) for func in KeyboardListener.on_presses]
                elif event == "keyup":
                    [func(ke) for func in KeyboardListener.on_releases]
                    
            return listener_inner

        KeyboardListener.listener = Listener(on_press=get_listener_func('keydown'), on_release=get_listener_func('keyup'))
        KeyboardListener.listener.start()
        
    def stop():
        """ Stops the listener thread. Does nothing if listener is not started. """
        if KeyboardListener.listener is not None:
            KeyboardListener.listener.stop()
            KeyboardListener.listener = None
            
    def is_held(identifier: NormalKey | SpecialKey) -> bool:
        """ Returns whether or not a key is currently held down. None if identifier is not found/supported. """
        return KeyboardListener.keys.get(identifier)
    
    def modifier_keys() -> Dict[str, bool]:
        """ 
        Returns a dict that specifies which modifier keys are held currently. Format:
        ```
        {
            "shift": bool
            "alt": bool
            "ctrl": bool
            "cmd": bool
        }
        """
        return {
            "shift": KeyboardListener.keys.get("shift") or KeyboardListener.keys.get("shift_l") or KeyboardListener.keys.get("shift_r"),
            "alt": KeyboardListener.keys.get("alt") or KeyboardListener.keys.get("alt_l") or KeyboardListener.keys.get("alt_r") or KeyboardListener.keys.get("alt_gr"),
            "ctrl": KeyboardListener.keys.get("ctrl") or KeyboardListener.keys.get("ctrl_l") or KeyboardListener.keys.get("ctrl_r"),
            "cmd": KeyboardListener.keys.get("cmd") or KeyboardListener.keys.get("cmd_l") or KeyboardListener.keys.get("cmd_r"),
        }