from render.utils import fcode
from logger import Logger
import blessed

class Rect:
    """
    Represents a rectangle on the screen at the specified position.
    """
    def __init__(self, left, top, right, bottom, term: blessed.Terminal, bg_color=None):
        """
        `bg_color` can be an rgb tuple or any 3/6-digit hex code (# optional)
        """
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.fcode = fcode(background=bg_color)
        self._term = term

    def render(self):
        
        width_px = (self.right - self.left) * self._term.width // 100

        with self._term.hidden_cursor():
            for y in range(min(self._term.height, 1+(self._term.height * (self.bottom - self.top) // 100))):
                print(self._term.move(self._term.height * self.top // 100 + y, self._term.width * self.left // 100) + f"{self.fcode} "*width_px)
                
class PxRect:
    """
    The same as `Rect` but corners must be defined by specific character positions.
    
    Draws from left, top to right-1, bottom-1
    
    For example, a fullscreen rect would have to go from
    (0, 0) to (term.width, term.height)
    """
    def __init__(self, left, top, right, bottom, term: blessed.Terminal, bg_color=None):
        """
        `bg_color` can be an rgb tuple or any 3/6-digit hex code (# optional)
        """
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.fcode = fcode(background=bg_color)
        self._term = term

    def render(self):

        with self._term.hidden_cursor():
            for y in range(self.top, self.bottom):
                print(self._term.move(y, self.left) + f"{self.fcode} "*(self.right - self.left), end="")