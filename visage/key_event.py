from typing import Literal

class KeyEvent:
    """ Represents a keyboard event that should be used as params in event handlers. """
    def __init__(self, key: str, state: Literal["keydown", "keyup"], is_special: bool):
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