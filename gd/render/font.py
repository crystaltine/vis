from typing import Dict
from logger import Logger
from PIL import Image
import numpy as np

class Font:
    """ Represents a monospaced font (parsed from images) that can be drawn to the screen. """
    
    PARSER_FORMAT = [
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "~`0123456789-_+=",
        "!@#$%^&*()[{]}|\;:'\",<.>/?",
    ]
    
    def __init__(self, path_to_font_png: str):
        """
        Initializes and loads each letter of the font into this object.
        
        # IMPORTANT FORMATTING INFO:
        Font PNGs MUST be formatted in the following way:
        Padding of 1px between ALL symbols. No padding on the outlines
        
        Symbols must be in the following order (newlines matter)
        (only one case supported as of now)
        ```
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        ~`0123456789-_+=
        !@#$%^&*()[{]}|\;:'",<.>/?
        ```
        
        Notes: This means font definition images should always be 25 + 26*font_width pixels wide, 
        and 3*font_height + 2 pixels tall. The font size that this function looks for is auto-calculated
        based on the image size. For example, if we find that the image is 155x20,
        we determine that 25+26w=155 => w=5, and 3h+2=20 => h=6.
        
        If the dimensions of the image do not conform to these dimensional constraints, this constructor raises an error.
        """
        
        self.fp = path_to_font_png
        self.symbols: Dict[str, np.ndarray] = {}
        """ Map of all symbols to their respective images, as 3D numpy arrays. """
        
        # load image into np arr
        img = np.array(Image.open(path_to_font_png))
        
        assert img.shape[0] % 3 == 2, "[Font/__init__]: Font image height must be 3n+2 (for some int n) pixels tall. Got: " + str(img.shape[0])
        assert img.shape[1] % 26 == 25, "[Font/__init__]: Font image width must be 26n+25 (for some int n) pixels wide. Got: " + str(img.shape[1])
        
        self.font_width = (img.shape[1] - 25) // 26
        """ Width of each character, in pixels """
        self.font_height = (img.shape[0] - 2) // 3
        """ Height of each character, in pixels """
        
        #Logger.log(f"img shape was {img.shape}, font width is {self.font_width}, font height is {self.font_height}")
        
        for i in range(len(Font.PARSER_FORMAT)):
            
            symbols_to_define = Font.PARSER_FORMAT[i]
            curr_row = img[i*self.font_height:(i+1)*self.font_height]
            #Logger.log(f"curr_row has shape {curr_row.shape}")
            
            for j in range(len(symbols_to_define)):
                self.symbols[symbols_to_define[j]] = curr_row[:, j*(self.font_width+1):(j+1)*(self.font_width+1)-1]
                #Logger.log(f"defining symbol {symbols_to_define[j]} as shape={self.symbols[symbols_to_define[j]].shape}")
                
        # lastly, define space as just an empty (0,0,0,0) array of same shape as the other symbols
        self.symbols[' '] = np.zeros_like(self.symbols['A'])
                
    def __getitem__(self, key: str) -> np.ndarray:
        """
        Returns the image of the symbol specified. KeyError if the symbol does not exist.
        
        Args:
            key: The character (e.g. "a", "*", etc.) to get the image of.
        """
        return self.symbols[key] 
    
    def get(self, key: str) -> np.ndarray:
        """
        Returns the image of the symbol specified. None if the symbol does not exist.
        
        Args:
            key: The character (e.g. "a", "*", etc.) to get the image of.
        """
        return self.symbols.get(key)