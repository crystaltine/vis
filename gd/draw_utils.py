import re
import os
from logger import Logger
from gd_constants import GDConstants

class Position:
    """
    Represents a position on the screen, defined in terms of ch, %, or calc() expressions.
    
    `top`, `left`, `bottom`, `right` represent the distance from the respective edge of the screen.
    For example, top=20% means the top of the element is 20% of the screen height from the top.
    """
    
    def __init__(self, left=None, top=None, right=None, bottom=None) -> "Position.Relative":
        """
        Returns a new Position object with all Nones, and by default is a `Position.Relative` object.
        """
        return Position.Relative(left, top, right, bottom)
    
    class Relative:
        """
        Position subclass that represents position in terms of percentages, characters, or calc() expressions.
        """
        def __init__(self, 
            top: str | int | None = None, 
            left: str | int | None = None, 
            bottom: str | int | None = None, 
            right: str | int | None = None):
            """
            Examples of valid values for params:
            - '50ch'
            - '50%'
            - 'calc(50% + 5ch)'
            - 50
            - None
            - 'calc(50% + 10 + 2% + 1ch)' (i hope this works lol)
            """
            self.top = top
            self.left = left
            self.bottom = bottom
            self.right = right
            
        def get_absolute(self, container_width: int = None, container_height: int = None) -> "Position.Absolute":
            """
            Returns the absolute values of the position, based on the container width and height.
            If container width or height is not provided, the GDConstants.term width and height will be used.
            """
            
            container_width = container_width or GDConstants.term.width
            container_height = container_height or GDConstants.term.height
            
            return Position.Absolute(
                top=convert_to_chars(container_height, self.top),
                left=convert_to_chars(container_width, self.left),
                bottom=convert_to_chars(container_height, self.bottom),
                right=convert_to_chars(container_width, self.right)
            )
            
        def __str__(self) -> str:
            return f"Position.Relative(t={self.top}, l={self.left}, b={self.bottom}, r={self.right})"
    
    class Absolute:
        """
        Position subclass where each field is an exact character value relative to the entire screen.
        """
        def __init__(self, 
            top: int | None = None, 
            left: int | None = None, 
            bottom: int | None = None, 
            right: int | None = None):
            """
            Examples of valid values for params:
            - 50
            - None
            """
            self.top = top
            self.left = left
            self.bottom = bottom
            self.right = right
            
        def __str__(self):
            return f"Position.Absolute(t={self.top}, l={self.left}, b={self.bottom}, r={self.right})"
    
STYLE_CODES = {
    'bold': '\033[1m',
    'italic': '\033[3m',
    'underline': '\033[4m',
    'dim': '\033[2m',
    'blink': '\033[5m',
    'reset': '\033[0m',
    'regular': '\033[0m',
    'none': '\033[0m',
    'default': '\033[0m',
}
PREDEFINED_COLORS = {
    "white": (255, 255, 255),
    "silver": (192, 192, 192),
    "gray": (128, 128, 128),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "maroon": (128, 0, 0),
    "yellow": (255, 255, 0),
    "olive": (128, 128, 0),
    "lime": (0, 255, 0),
    "green": (0, 128, 0),
    "aqua": (0, 255, 255),
    "teal": (0, 128, 128),
    "blue": (0, 0, 255),
    "navy": (0, 0, 128),
    "fuchsia": (255, 0, 255),
    "purple": (128, 0, 128)
}
def fcode(foreground: str | tuple[int] = None, background: str | tuple[int] = None, style: str = None) -> str:
    '''
    Returns an ANSI format string matching the given styles. This may not be supported in all terminals.
    
    ## Parameters
    
    `foreground` and `background`: can be hex code (with or without `#`), a 3-tuple of rgb values, or a predefined supported colorname (see `PREDEFINED_COLORS`).
    - `'#ff00ff'` (regular hex code)
    - `'d208c7'` (no hashtag)
    - `'#cd3'` (short hex code, 4 bit color)
    - `'778'` (short hex code without hashtag)
    - `(255, 0, 255)` (standard rgb tuple)
    - 'fuchsia' (supported color name - see `PREDEFINED_COLORS`)
    
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
    
    Having that `RS` code at the end is technically optional but without it the formatting will continue to be used by the GDConstants.term.
    
    *Note that it seems that the bold style does not seem to be supported on some terminals (notably Windows Terminal).
    '''
    
    format_str = ''
    
    if foreground is not None:
        
        if foreground in PREDEFINED_COLORS:
            foreground = PREDEFINED_COLORS[foreground]
            
        elif isinstance(foreground, str):
            # get rid of hashtag if it exists
            foreground = foreground[1:] if foreground[0] == '#' else foreground
            
            # if the hex is 3 characters long, expand it to 6.
            if len(foreground) == 3:
                foreground = foreground[0] * 2 + foreground[1] * 2 + foreground[2] * 2
            
            # parse rgb
            foreground = tuple(int(foreground[i:i+2], 16) for i in range(0, 6, 2))
        
        format_str += '\033[38;2;{};{};{}m'.format(*foreground)
        
    if background is not None and background != 'transparent':
        
        if background in PREDEFINED_COLORS:
            background = PREDEFINED_COLORS[background]
            
        elif isinstance(background, str):
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

def cls() -> None:
    """
    Clears the terminal using 'cls'

    @TODO - uh i forgot how to check for OS names, idk if cls works everywhere. works on ps win11 tho.
    """
    os.system('cls')

def print2(*args, **kwargs) -> None:
    """
    Wrapper for builtin print that always has end="\\r\\x1b[0m"
    """
    print(*args, **kwargs, end='\r\x1b[0m')

def convert_to_chars(container_dim: int, dimvalue: int | str | None) -> int | None:
    """
    Returns the actual value of the dimension (in characters) based on the container size,
    or `None` if the given value is None.
    
    `dimvalue` must be a string of the following formats:
    - raw number, either as int or str (e.g. 123 or '123')
    - number ending in 'ch' (e.g. '123ch')
    - number ending in 'px' (e.g. '123px')
    - number ending in '%' (e.g. '12%')
    - expression using the function 'calc()'. Inside the expression, use '+' or '-' (no * or /)
      between two of the above values (e.g. 50% + 5, 25% + 12ch)
    
    `container_dim`: the size of the container in the dimension we're calculating.
    
    examples:
    - `convert_to_chars(232, None) -> None`
    - `convert_to_chars(120, '50%') -> 60`
    - `convert_to_chars(120, '324234ch') -> 324234` (why would you do this)
    """
    
    if dimvalue is None: return None
    
    # if int, assume as raw character value
    if isinstance(dimvalue, int) or (isinstance(dimvalue, str) and dimvalue.isnumeric()): return int(dimvalue)
    
    # if float, round to int
    if isinstance(dimvalue, float): return round(dimvalue)
    
    # check if str is calc expr
    if dimvalue.startswith("calc("):
        # take chars from idx 5->-2, inclusive
        return evaluate_expression(container_dim, dimvalue[5:-1])
    
    if dimvalue[-2:] in ('px', 'ch'):
        return int(float(dimvalue[:-2]))
    elif dimvalue[-1] == '%':
        return round(container_dim * int(float(dimvalue[:-1])) / 100)
    else:
        raise ValueError(f"Invalid dimvalue: {dimvalue}. Must end in 'ch' or '%'.")    

def evaluate_expression(container_dim: int, expr: str) -> int:
    """
    Evaluates string expressions inside `calc()`.
    For example, `calc(50% + 5)` would return 55 (50 + 5) if `container_dim` is 100.
    """
    # remove extra spaces
    expr = re.sub(' +', ' ', expr)
    tokens = expr.split(" ")
    
    #Logger.log(f"eval expr: tokens is {tokens} (expr was {expr})")
    #Logger.log(f"eval expr: tokens is {tokens} (expr was {expr})")
    
    if len(tokens) < 3 or len(tokens) % 2 == 0:
        raise ValueError(f"Invalid calc() expression: {expr}. Must have at least n>=2 operands and n-1 operators.")
    
    #Logger.log(f"a,b are gonna be {convert_to_chars(container_dim, tokens[0])}, {convert_to_chars(container_dim, tokens[2])}")
    #Logger.log(f"type of a,b: {type(convert_to_chars(container_dim, tokens[0]))}, {type(convert_to_chars(container_dim, tokens[2]))}")
    #Logger.log(f"a,b are gonna be {convert_to_chars(container_dim, tokens[0])}, {convert_to_chars(container_dim, tokens[2])}")
    #Logger.log(f"type of a,b: {type(convert_to_chars(container_dim, tokens[0]))}, {type(convert_to_chars(container_dim, tokens[2]))}")
    # expect first token to be a value, not an operator
    operator = lambda a,b:(a+b if tokens[1] == "+" else a-b)
    return operator(convert_to_chars(container_dim, tokens[0]), convert_to_chars(container_dim, tokens[2]))

def draw_rect(
    color: str | tuple, 
    position: Position.Relative, 
    width: int | str | None = None, 
    height: int | str | None = None,
    outline_color: str | tuple | None = None) -> None:
    """
    Draws a rectangle given the position and dimensions.
    
    `color` - hex code, rgb tuple, or predefined color name (see `fcode` method)

    ### Positioning
    
    Important: If two controlling values are provided in `position`, such as `top` and `bottom`, the `height` parameter will be ignored.
    Basically, height and width params are only used if `position` only specifies one of the two dimensions, such as if `bottom` is None.
    
    If none of a dimension's controlling values are provided (`top` and `bottom` must not both be None, for example), an error will be thrown.
    
    ### Outlines
    If `outline_color` is provided (not None), then 1 half-character (1 pixel, equivalent to 1 monospace char width and 1/2 monospace char height)
    will be drawn around the rectangle. THIS DOES NOT EXPAND THE RECTANGLE - 
    """
    
    # TODO - implement outlining
    
    # convert width and height to characters if they are not already
    #Logger.log(f"draw_rect: width, height: {width}, {height}")
    conv_width = convert_to_chars(GDConstants.term.width, width) if width is not None else GDConstants.term.width
    conv_height = convert_to_chars(GDConstants.term.height, height) if height is not None else GDConstants.term.height
    #Logger.log(f"^^ converted width, height: {conv_width}, {conv_height}")
    
    abs_pos = position.get_absolute(GDConstants.term.width, GDConstants.term.height)
    
    # assert that at least one of the two dimensions is specified
    if position.top is None and position.bottom is None:
        raise ValueError("At least one of top or bottom must be specified in position.")
    
    if position.left is None and position.right is None:
        raise ValueError("At least one of left or right must be specified in position.")
    
    # find true top and left values
    #Logger.log(f"conv_height, conv_width: {conv_height}, {conv_width}")
    #Logger.log(f"conv_height, conv_width: {conv_height}, {conv_width}")
    true_top = abs_pos.top if abs_pos.top is not None else GDConstants.term.height - abs_pos.bottom - conv_height
    true_left = abs_pos.left if abs_pos.left is not None else GDConstants.term.width - abs_pos.right - conv_width
    
    # find true width and height
    true_width = GDConstants.term.width - abs_pos.right - abs_pos.left if (abs_pos.left is not None and abs_pos.right is not None) else conv_width
    true_height = GDConstants.term.height - abs_pos.bottom - abs_pos.top if (abs_pos.top is not None and abs_pos.bottom is not None) else conv_height
    
    #Logger.log(f"drawing rect from row,col= {true_top}, {true_left} to {true_top+true_height}, {true_left+true_width}")
    #Logger.log(f"abs_pos: {abs_pos}")
    #Logger.log(f"draw_rect position: {position}")
    #Logger.log(f"true_width, true_height: {true_width}, {true_height}")
    #Logger.log(f"conv_width, conv_height: {conv_width}, {conv_height}, width, height: {width}, {height}")
    #Logger.log(f"color: {color}\n")
    
    # draw the rectangle
    for i in range(true_top, true_top + true_height):
        print2(GDConstants.term.move_yx(i, true_left) + fcode(color) + "█"*true_width)

def colorize_pixel(grayscale_value: int, primary_color: str | tuple, secondary_color: str | tuple) -> tuple:
    """
    Applies color to a grayscale pixel based on the primary and secondary colors. Primary color attempts to replace dark
    pixels, secondary color replaces light pixels. A basic gradient is used to combine the two colors for gray-ish pixels.
    
    Grayscale value should be an int between 0 and 255, the value for all RGB channels in the pixel. This function assumes
    that the pixel is actually gray.
    
    Blending function used: weighted average
    
    Outputs a tuple of RGB values for the colorized pixel.
    """
    
    secondary_weight = grayscale_value / 255
    primary_weight = 1 - secondary_weight
    
    # blend the two colors
    r = int(primary_color[0]*primary_weight + secondary_color[0]*secondary_weight)
    g = int(primary_color[1]*primary_weight + secondary_color[1]*secondary_weight)
    b = int(primary_color[2]*primary_weight + secondary_color[2]*secondary_weight)
    
    Logger.log(f"colorized pixel: value={grayscale_value}, primary={primary_color}, secondary={secondary_color}, result={r,g,b}")
    return (r, g, b)

def hex_to_rgb(hex_color: str) -> tuple:
    """
    Converts a hex color to an RGB tuple. Hex color should be in the format "#RRGGBB" or "RRGGBB".
    """
    if len(hex_color) == 7:
        hex_color = hex_color[1:]
        
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color: tuple) -> str:
    """
    Converts an RGB tuple to a hex color. Output is in the format "#RRGGBB".
    """
    return f"#{''.join(f'{c:02x}' for c in rgb_color)}"
