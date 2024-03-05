import os

""" commented out cuz school comps have py 3.7 and these unions are causing errors :skull:
def fcode(foreground: str | tuple[int] = None, background: str | tuple[int] = None, style: str = None) -> str:
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
    
    `style`: a space-separated string which can contain any of the following styles:
    - any of `'reset'`, `'regular'`, `'none'`, `'default'` - no style. OVERRIDES ALL OTHER STYLES AND COLORS.
    - `'bold'`
    - `'italic'`
    - `'underline'`
    - `'dim'`
    - `'blink'`
    
    If omitted, no changes in styling will be applied.
    
    Any other words will be ignored.
    
    ## Example
    ```python
    RS = '\\033[0m'
    print(f'{fcode('ff00ff', 'ffff00', style='bold')}Hello, world!{RS}')
    ```
    
    This will print 'Hello, world!' in bold* magenta with a yellow background.
    
    Having that `RS` code at the end is technically optional but without it the formatting will continue to be used by the terminal.
    
    *Note that it seems that the bold style does not seem to be supported on some terminals (notably Windows Terminal).
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
        
    if style is not None:
        style_format_string = ''
        
        # split style string
        styles = style.split(' ')
        
        # for each style, add the format code to the format string
        for style in styles:
            # if style is reset, ignore all other styles and just return the reset code
            if style.lower() in ('reset', 'regular', 'none', 'default'):
                return '\033[0m'
            style_format_string += STYLE_CODES.get(style.lower(), '')
            
        format_str += style_format_string
    
    return format_str
"""

def cls():
    """
    Clears the terminal using 'cls'

    @TODO - uh i forgot how to check for OS names, idk if cls works everywhere. works on ps win11 tho.
    """
    os.system('cls')