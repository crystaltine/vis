from typing import Dict, List, TYPE_CHECKING
from utils import fcode_opt as fco

if TYPE_CHECKING:
    from blessed import Terminal

class CameraFrame:
    """
    Wrapper over a set of 2d (numpy?) arrays that stores a frame to be rendered to the screen.

    Supports layers. 
    """

    def __init__(self, term: "Terminal")
        self.term = term

        self.layers: Dict[str, List[List[Pixel]]] = {}
        """ Dict of {Layer name : 2d list of pixels that are in that layer} """

class Pixel:
    """
    Represents a single pixel in the screen, which is half of a monospaced character.

    Stores data on the color and whether or not it is the top half or bottom half of a character.
    """

    def __init__(self, color: tuple, is_top_half: bool) -> None:
        self.color = color
        """ Should be a rgb(a?)255 tuple ONLY (got rid of hexcode for optimization) """

        self.is_top_half = is_top_half

    def compile_to_char(self, other: "Pixel") -> str:
        """
        Combines this pixel with another to create a colored character (block element)
        with ANSI color codes. Make sure other is the other half of the character (both cant be the same half)
        
        For optimization, the string this function returns does not have a format reset code at the end,
        meaning all formatting will carry to the next char unless it specifies otherwise (which it should)
        """
        if self.is_top_half == other.is_top_half:
            raise ValueError(f"[Pixel/compile_to_char] Cannot compile pixels that both have is_top_half={self.is_top_half}")

        color_code = fco(fg=self.color,bg=other.color) if self.is_top_half else fco(fg=other.color,bg=self.color)

        return color_code + "▀"