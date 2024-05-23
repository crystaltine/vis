from typing import Union, Tuple
import re
import os

def fcode(fg: Union[str, tuple] = None, bg: Union[str, tuple] = None) -> str:
    '''
    Returns an ANSI format string matching the given styles. This may not be supported in all terminals.
    
    ## Parameters
    
    `fg` and `bg`: can be hex code (with or without `#`) or a 3-tuple of rgb values. Examples:
    - `'#ff00ff'` (regular hex code)
    - `'d208c7'` (no hashtag)
    - `'#cd3'` (short hex code, 4 bit color)
    - `'778'` (short hex code without hashtag)
    - `(255, 0, 255)` (standard rgb tuple)
    
    If either are omitted, the default color will be used. (probably white for fg, and transparent for bg)
    
    Custom styling (italic, etc) is dropped in this implementation.
    
    ## Example
    ```python
    RS = '\\033[0m'
    print(f'{fcode('ff00ff', 'ffff00')}Hello, world!{RS}')
    ```
    
    This will print 'Hello, world!' in magenta with a yellow bg.
    
    Having that `RS` code at the end is technically optional but without it the formatting will continue to be used by the terminal.
    '''
    
    format_str = ''
    
    if fg is not None:
        
        if isinstance(fg, str):
            # get rid of hashtag if it exists
            fg = fg[1:] if fg[0] == '#' else fg
            
            # if the hex is 3 characters long, expand it to 6.
            if len(fg) == 3:
                fg = fg[0] * 2 + fg[1] * 2 + fg[2] * 2
            
            # parse rgb
            fg = tuple(int(fg[i:i+2], 16) for i in range(0, 6, 2))
        
        format_str += '\033[38;2;{};{};{}m'.format(*fg)
        
    if bg is not None:
            
        if isinstance(bg, str):
            # get rid of hashtag if it exists
            bg = bg[1:] if bg[0] == '#' else bg
            
            # if the hex is 3 characters long, expand it to 6.
            if len(bg) == 3:
                bg = bg[0] * 2 + bg[1] * 2 + bg[2] * 2
            
            # parse rgb
            bg = tuple(int(bg[i:i+2], 16) for i in range(0, 6, 2))
        
        format_str += '\033[48;2;{};{};{}m'.format(*bg)
    
    return format_str
fc = fcode
""" Alias for `fcode` method. """

def fcode_opt(fg: Tuple[int, int, int] = None, bg: Tuple[int, int, int] = None) -> str:
    '''
    Optimized version of `fcode` (see docs for that) - BUT:
    - only accepts 3-tuples for colors
    - no letter styling (bold, italic, etc.)
    - no predefined color names
    Mainly used for drawing block elements (pixels) in the terminal.
    '''
    
    format_str = ''
    
    if fg is not None:
        format_str += '\033[38;2;{};{};{}m'.format(*fg)
    if bg is not None:
        format_str += '\033[48;2;{};{};{}m'.format(*bg)
        
    return format_str

fco = fcode_opt
""" Alias for `fcode_opt` method """

def mix_colors(color1: Union[str, tuple], color2: Union[str, tuple], amount: float) -> str:
    """
    Mixes colors, with amount being a float from 0 to 1: 0 is closest to color1, 1 is closest to color2.
    Returns a hex color, of the format `#rrggbb`.
    
    Input format: either a hex string of the format `#rrggbb`, `rrggbb` or a 3-tuple of rgb values.
    """
    
    # convert hex to rgb
    if isinstance(color1, str):
        if len(color1) == 7: color1 = color1[1:]
        color1 = tuple(int(color1[i:i+2], 16) for i in range(0, 6, 2))
    if isinstance(color2, str):
        if len(color2) == 7: color2 = color2[1:]
        color2 = tuple(int(color2[i:i+2], 16) for i in range(0, 6, 2))
        
    # mix colors
    mixed = tuple(int(color1[i] + (color2[i] - color1[i]) * amount) for i in range(3))
    
    # convert rgb to hex
    return '#' + ''.join(hex(i)[2:].zfill(2) for i in mixed)    

def cls():
    """
    Clears the terminal using 'cls'

    @TODO - uh i forgot how to check for OS names, idk if cls works everywhere. works on ps win11 tho.
    """
    os.system('clear')

def len_no_ansi(string: str) -> str:
    """
    @see - https://github.com/chalk/ansi-regex/blob/0755e661553387cfebcb62378181e9f55b2567ff/index.js
    """
    return len(re.sub(
        r'[\u001B\u009B][\[\]()#;?]*((([a-zA-Z\d]*(;[-a-zA-Z\d\/#&.:=?%@~_]*)*)?\u0007)|((\d{1,4}(?:;\d{0,4})*)?[\dA-PR-TZcf-ntqry=><~]))', '', string))

def remove_ansi(string: str) -> str:
    """
    @see - https://github.com/chalk/ansi-regex/blob/0755e661553387cfebcb62378181e9f55b2567ff/index.js
    """
    return re.sub(
        r'[\u001B\u009B][\[\]()#;?]*((([a-zA-Z\d]*(;[-a-zA-Z\d\/#&.:=?%@~_]*)*)?\u0007)|((\d{1,4}(?:;\d{0,4})*)?[\dA-PR-TZcf-ntqry=><~]))', '', string)
    
def closest_quarter(x: float) -> float:
    """
    Returns the (positive) quarter that's closest to x. 
    Supports negative numbers too!
    
    Only returns something in `[0, 0.25, 0.5, 0.75]`
    
    Examples:
    - `0.1` -> `0`
    - `74.3` -> `0.25`
    - `-199.6` -> `0.5`
    """
    # Extract the decimal part of x
    decimal_part = abs(x - int(x))
    
    # Define the quarters
    quarters = [0, 0.25, 0.5, 0.75]
    
    # Find the closest quarter to the decimal part
    closest = min(quarters, key=lambda q: abs(decimal_part - q))
    
    return closest

def nearest_quarter(x: float) -> float:
    """
    Returns the nearest quarter to x. 
    Supports negative numbers too!
    
    Examples:
    - `0.1` -> `0`
    - `2.99` -> `3.0`
    - `-1.13` -> `-1.25`
    - `-1.12` -> `-1.0`
    """
    return round(x * 4) / 4