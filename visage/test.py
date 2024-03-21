from pynput import keyboard
from time import sleep
import blessed

class KeyEvent:
    """ Represents a keyboard event that should be used as params in event handlers. """
    def __init__(self, key: str, state: str, is_special: bool):
        self.key = key
        self.state = state
        self.is_special = is_special
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
        return f"KeyEvent('{self.key}',{self.state},special={self.is_special},canceled={self.canceled}"

term = blessed.Terminal()

def on_press(_key: keyboard.Key):

    ev = ...
    if isinstance(_key, keyboard.KeyCode):
        ev = KeyEvent(_key.char, "keydown", False)
    else:
        # handle space - its treated as special due to smth
        if _key.name == "space": ev = KeyEvent(" ", "keydown", False)
        else: ev = KeyEvent(_key.name, "keydown", True)

    print(ev)
    print(keyboard.Key.shift)

def on_release(key):
    print(f'{key} released, type={type(key)}')
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

#for i in range(5, term.height-5):
#    with term.location(10, i):
#        print(f"\033[48;2;63;129;189m" + " "*(term.width-20), end="")
        
#with term.location(20, 20):
#    a = input("\033[38;2;255;255;0m\033[48;2;144;144;144m")

#print(a + " < u typed this")