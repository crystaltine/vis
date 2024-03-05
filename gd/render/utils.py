import blessed
from typing import Union

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
