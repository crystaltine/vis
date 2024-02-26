import curses
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from element import Element

class Document:
    """
    Represents a "document" (terminal screen), similar to the DOM in HTML.

    Creating an object handles curses initialization.
    """

    def __init__(self):
        """
        Initializes curses screen.

        Also sets:
        - noecho
        - cbreak mode
        - disables blinking cursor
        - enables colors if available
        """
        self.screen = curses.initscr()
        self.id_map: Dict[str, List["Element"]] = {}
        """ id : [element object] (supports repeat IDs) """

        self.elements: List["Element"] = []
        """ General, ordered elements list. Contains all elements in `self.id_map` too. """

         # dont echo keys back to the client
        curses.noecho()

        # Non-blocking or cbreak mode: dont wait for enter key press
        curses.cbreak()

        # disable cursor (we will probably use a custom one)
        curses.curs_set(False)

        # enable colors if available
        if curses.has_colors():
            curses.start_color()

    def get_element_by_id(self, id: str, index: int = None) -> "Element" | List["Element"] | None:
        """
        Get the element object(s) with specified ID.

        If multiple elements have the same ID:
        - if `index` is provided, return the one at `index`.
        - if `index` is not provided, return a list of all of them.
        
        Returns `None` if no elements have the specified ID.
        """
        _element_list = self.id_map.get(id)

        if _element_list is None or len(_element_list) == 0:
            return None

        return _element_list[index]

    def add_element(self, element: "Element"):
        """
        Adds a root-level element to the DOM. 
        """

        # add to general list
        self.elements.append(element)

        if element.id is not None:
            # add to id map
            curr_list_at_id = self.id_map.get(element.id)
            
            # if curr list is None, create
            if curr_list_at_id is None: self.id_map[element.id] = [element]
            else: self.id_map[element.id].append(element)

    def mount():
        """
        Mounts
        """