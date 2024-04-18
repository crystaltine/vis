from typing import Union
import re
import os

def fcode(foreground: Union[str, 'tuple[int]'] = None, background: Union[str, 'tuple[int]'] = None) -> str:
    '''
    Returns an ANSI format string matching the given styles. This may not be supported in all terminals.
    
    ## Parameters
    
    `foreground` and `background`: can be hex code (with or without `#`) or a 3-tuple of rgb values. Examples:
    - `'#ff00ff'` (regular hex code)
    - `'d208c7'` (no hashtag)
    - `'#cd3'` (short hex code, 4 bit color)
    - `'778'` (short hex code without hashtag)
    - `(255, 0, 255)` (standard rgb tuple)
    
    If either are omitted, the default color will be used. (probably white for foreground, and transparent for background)
    
    Custom styling (italic, etc) is dropped in this implementation.
    
    ## Example
    ```python
    RS = '\\033[0m'
    print(f'{fcode('ff00ff', 'ffff00')}Hello, world!{RS}')
    ```
    
    This will print 'Hello, world!' in magenta with a yellow background.
    
    Having that `RS` code at the end is technically optional but without it the formatting will continue to be used by the terminal.
    '''
    
    format_str = ''
    
    if foreground is not None:
        
        if isinstance(foreground, str):
            # get rid of hashtag if it exists
            foreground = foreground[1:] if foreground[0] == '#' else foreground
            
            # if the hex is 3 characters long, expand it to 6.
            if len(foreground) == 3:
                foreground = foreground[0] * 2 + foreground[1] * 2 + foreground[2] * 2
            
            # parse rgb
            foreground = tuple(int(foreground[i:i+2], 16) for i in range(0, 6, 2))
        
        format_str += '\033[38;2;{};{};{}m'.format(*foreground)
        
    if background is not None:
            
        if isinstance(background, str):
            # get rid of hashtag if it exists
            background = background[1:] if background[0] == '#' else background
            
            # if the hex is 3 characters long, expand it to 6.
            if len(background) == 3:
                background = background[0] * 2 + background[1] * 2 + background[2] * 2
            
            # parse rgb
            background = tuple(int(background[i:i+2], 16) for i in range(0, 6, 2))
        
        format_str += '\033[48;2;{};{};{}m'.format(*background)
    
    return format_str

def cls():
    """
    Clears the terminal using 'cls'

    @TODO - uh i forgot how to check for OS names, idk if cls works everywhere. works on ps win11 tho.
    """
    os.system('cls')

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