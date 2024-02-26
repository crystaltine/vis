from abc import ABC, abstractmethod
from typing import List
import curses

from tss import TSSProperties

class Element(ABC):
    """
    A Generic, abstract element class for the vis document.
    """

    def __init__(self, children: List["Element"] = [], style: TSSProperties = None):
        """
        Creates an element with the option to init with children and styles.
        """

        self.children = children
        self.style = style
        self.targetable: bool = not (self.style.get("user-select") == 'none') # only false if explicitly 'none'
        self.is_targeted = False # if it is currently selected

        self.window_obj = curses


        # These will be initialized once the element is mounted
        self.client_left = None
        self.client_top = None
        self.client_width = None
        self.client_height = None