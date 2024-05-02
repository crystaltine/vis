from typing import Literal
from pynput.keyboard import Key, KeyCode
from blessed.keyboard import Keystroke

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

class KeyEvent:
    """
    Represents a keyboard event detected through `pynput`.
    """
    
    holding_shift = False
    """ True if any shift key is currently being held. 
    Note that shift being held will cause character KeyEvents to change (e.g. `5` -> `%`). """
    holding_ctrl = False
    """ True if any ctrl key is currently being held. """
    holding_alt = False
    """ True if any alt key is currently being held. """
    holding_cmd = False
    """ True if any cmd key is currently being held. """
    
    """ Represents a keyboard event that should be used as params in event handlers. """
    def __init__(self, key: SpecialKey | str, state: Literal["keydown", "keyup"], is_special: bool):
        self.key: SpecialKey | str = key
        """
        If the KeyEvent is just a character, this is probably a string of length 1 ("a", "G", "7", "*", etc).
        
        If special, then one of the following:
        - at least a modifier key is held (shift, ctrl, alt, etc.)
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
        self.state = state
        """ Either "keydown" or "keyup". """
        self.is_special = is_special
        self.canceled = False
        
        # set a snapshot of the current state of the modifier keys
        self.ctrl = KeyEvent.holding_ctrl
        self.alt = KeyEvent.holding_alt
        self.shift = KeyEvent.holding_shift
        self.cmd = KeyEvent.holding_cmd
        
    def cancel(self) -> None:
        """
        Stop the propogation of the event. This is only reliable
        if being called inside an element's event handlers, since document
        event handlers are "unordered" sets.

        Note that the selected element's event handlers are run before
        the document's handlers.
        """
        self.canceled = True

    def __str__(self) -> str:
        """ Returns a human readable string representation of the event. """
        cancel_string = '\x1b[31mcanceled\x1b[0m' if self.canceled else '\x1b[32mnot canceled\x1b[0m'
        mods = []
        mods.append('ctrl') if self.holding_ctrl else 0
        mods.append('alt') if self.holding_alt else 0
        mods.append('shift') if self.holding_shift else 0
        mods.append('cmd') if self.holding_cmd else 0

        return f"KeyEvent(\x1b[32m'{self.key}'\x1b[0m,\x1b[33m{self.state}\x1b[0m,special=\x1b[33m{self.is_special}\x1b[0m,{cancel_string},modifiers=\x1b[34m{mods}\x1b[0m)"


    
    @staticmethod
    def update_modifiers(key_event: "Key | KeyCode", state: Literal["keydown", "keyup"]) -> None:
        """
        Updates the current pressed-state of the modifier keys (shift, ctrl, alt, cmd) 
        based on the given key event and whether or not it was a keydown or keyup event.
        
        Does nothing besides updating this class's fields. If no states were changed, does absolutely nothing.
        """
        
        if isinstance(key_event, KeyCode): return # these are non-special keys
        
        set_things_to = state == "keydown" # True if keydown, False if keyup
        
        match key_event.name:
            case "ctrl" | "ctrl_l" | "ctrl_r":
                KeyEvent.holding_ctrl = set_things_to
            case "alt" | "alt_l" | "alt_r" | "alt_gr":
                KeyEvent.holding_alt = set_things_to
            case "shift" | "shift_l" | "shift_r":
                KeyEvent.holding_shift = set_things_to
            case "cmd" | "cmd_l" | "cmd_r":
                KeyEvent.holding_cmd = set_things_to
            case default:
                pass
    
    @staticmethod 
    def create_from(key_event: "Key | KeyCode") -> "KeyEvent":
        """
        Creates a KeyEvent from a pynput key event.
        """
        ev = ...
        if isinstance(key_event, KeyCode):
            ev = KeyEvent(key_event.char, "keydown", False)
        else: # should be Key object
            # handle space - its treated as special due to smth
            if key_event.name == "space": ev = KeyEvent(" ", "keydown", False)
            else: ev = KeyEvent(key_event.name, "keydown", True)
        
        # set a snapshot of the current state of the modifier keys
        ev.ctrl = KeyEvent.holding_ctrl
        ev.alt = KeyEvent.holding_alt
        ev.shift = KeyEvent.holding_shift
        ev.cmd = KeyEvent.holding_cmd
        return ev
    
class KeyEvent2:
    """
    Represents a keyboard event detected through `blessed.keyboard`. Similar to `KeyEvent`
    but this one can only see keydowns and can't tell you if any of the special keys are being held (sad)
    
    However special keys like `ctrl+[key]` will still be marked as `is_special`, but theyll look something like `\\x08`
    """

    """ Represents a keyboard event that should be used as params in event handlers. """
    def __init__(self, key: str, name: str | None, is_special: bool):
        self.key: str = key
        """
        If the KeyEvent is just a character, this is probably a string of length 1 ("a", "G", "7", "*", etc).
        
        If special, then this will be something like
        `\\x08` (`ctrl+h`)
        `\\x1b` (`esc`)
        """
        
        self.name = name
        """
        Only isn't None for a few special keys.        
        See the full list at https://blessed.readthedocs.io/en/latest/keyboard.html#keycodes
        
        Some important/common ones:
        - 'KEY_F1' all the way to 'KEY_F12' (even until F23 on some keyboards)
        - 'KEY_BACKSPACE', 'KEY_DELETE', 'KEY_INSERT'
        - 'KEY_ENTER'
        - 'KEY_ESCAPE'
        - 'KEY_TAB', 'KEY_BTAB' (shift+tab)
        - 'KEY_DOWN' (all arrow keys: LEFT, RIGHT, UP, DOWN)
        """
        
        self.is_special = is_special
        """ A key is special if it is not alphanumeric, a symbol, or a space. """
        
        self.canceled = False
        
    def cancel(self) -> None:
        """
        Stop the propogation of the event. This is only reliable
        if being called inside an element's event handlers, since document
        event handlers are "unordered" sets.

        Note that the selected element's event handlers are run before
        the document's handlers.
        """
        self.canceled = True

    def __str__(self) -> str:
        """ Returns a human readable string representation of the event. """
        cancel_string = '\x1b[31mcanceled\x1b[0m' if self.canceled else '\x1b[32mnot canceled\x1b[0m'

        return f"KeyEvent2(\x1b[32mkey={self.key} specialname={self.name}\x1b[0m,special=\x1b[33m{self.is_special}\x1b[0m,{cancel_string})"
    
    @staticmethod 
    def create_from(key_event: "Keystroke") -> "KeyEvent2":
        """
        Creates a KeyEvent from a blessed KeyStroke object.
        """
        ev = ...
        if key_event.is_sequence: # special key
            ev = KeyEvent2(str(key_event), key_event.name, True)
        else: # regular key
            ev = KeyEvent2(str(key_event), None, False)
            
        return ev