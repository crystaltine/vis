import os
import sys
import re
import json
from typing import Set, TYPE_CHECKING
from globalvars import Globals
from logger import Logger

if TYPE_CHECKING:
    from element import Element
    from key_event import KeyEvent2

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
    
    Having that `RS` code at the end is technically optional but without it the formatting will continue to be used by the terminal.
    
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
    
def parseattrs(object, provided_opts: dict | None, default: dict) -> None:
    """
    Looks at `provided_opts` and, for every key in `provided_opts` that also appears in `default`,
    sets the associated value as a field on `object`, using the value from `default` if not provided.
    """
    
    if provided_opts is None:
        provided_opts = {}
    
    for key in default:
        
        # print(f"\x1b[34mparseattr: setting {key} to {provided_opts.get(key, default[key])} on {object}\x1b[0m")
        setattr(object, key, provided_opts.get(key, default[key]))
 
def convert_to_chars(container_dim: int, dimvalue: int | str | None) -> int | None:
    """
    Returns the actual value of the dimension (in characters) based on the container size,
    or `None` if the given value is None.
    
    `dimvalue` must be a string of the following formats:
    - raw number, either as int or str (e.g. 123 or '123')
    - number ending in 'ch' (e.g. '123ch')
    - number ending in '%' (e.g. '12%')
    - expression using the function 'calc()'. Inside the expression, use '+' or '-' 
      between two of the above values (e.g. 50% + 5, 25% + 12ch)
    
    `container_dim`: the size of the container in the dimension we're calculating.
    
    examples:
    - `convert_to_chars(232, None) -> None`
    - `convert_to_chars(120, '50%') -> 60`
    - `convert_to_chars(120, '324234ch') -> 324234` (why would you do this)
    """
    
    if dimvalue is None: return None
    
    # if int, assume as raw character value
    if isinstance(dimvalue, int) or dimvalue.isnumeric(): return dimvalue
    
    # check if str is calc expr
    if dimvalue.startswith("calc("):
        # take chars from idx 5->-2, inclusive
        return evaluate_expression(dimvalue[5:-1])
    
    if dimvalue[-2:] == 'ch':
        return int(dimvalue[:-2])
    elif dimvalue[-1] == '%':
        return round(container_dim * int(dimvalue[:-1]) / 100)
    else:
        raise ValueError(f"Invalid dimvalue: {dimvalue}. Must end in 'ch' or '%'.")    

def evaluate_expression(container_dim: int, expr: str) -> int:
    # remove extra spaces
    expr = re.sub(' +', ' ', expr)
    tokens = expr.split(" ")
    
    # expect first token to be a value, not an operator
    operator = lambda a,b:(a+b if tokens[1] == "+" else a-b)
    return operator(convert_to_chars(container_dim, tokens[0]), convert_to_chars(container_dim, tokens[2]))
    
def parse_style_string(style_str: str) -> dict[str, str]:
    """
    Parses a style string into a `Dict` using `json.loads`.
    This will throw a `json.JSONDecodeError` if the string is not valid JSON.
    
    @TODO - allow more flexible css-like style strings.
    """
    if not style_str: return {}
    
    #print(f"\x1b[34mJSON.loadsing string: {style_str}\x1b[0m")
    
    return json.loads(style_str)

def parse_class_string(class_str: str) -> dict:
    """
    Looks for the class names in the global scope and returns a dict of compiled styles.
    
    ### Note:
    Classnames that appear earlier in the string take precedence over those that appear later.
    """
    # for each class_str, look for it in globals. if exists, get the associated styledict.
    # then merge them together with the earliest taking precedence.
    class_strings = class_str.split(" ")
    parsed_style = {}
    
    for i in range(len(class_strings)-1, -1, -1):
        # we go in reverse so that the ones in front overwrite the ones in back
        if class_strings[i] in Globals.__class_styles__:
            parsed_style |= Globals.__class_styles__[class_strings[i]]
    
    #print(f"\x1b[35mClassstr parser: {class_str=}, {parsed_style=}, __class_styles__={Globals.__class_styles__}\x1b[0m")
    return parsed_style

def calculate_style(style_str: str, class_str: str, default_style: dict) -> dict:
    """
    Returns a dict of styles that is a merge of the explicitly set style, class styles, and default style.
    Order of precedence: explicitly set style > class styles > default style.
    
    For optimization, this should be used on init of an element, and on every change to its classstr or stylestr.
    """
    #print(f"\x1b[34mCalc_style: {style_str=}, {class_str=}, {default_style=}\x1b[0m")
    return default_style | parse_class_string(class_str) | parse_style_string(style_str)

def get_next_hoverable(hoverable_elements: Set["Element"], currently_hovered: "Element | None", key_ev: "KeyEvent2") -> "Element":
    """
    Given a set of hoverable elements, the currently hovered element, and a key, returns the next element to hover.
    
    Throws a ValueError if the key event is not valid for selecting elements.
    It should be in `['up', 'down', 'left', 'right', 'tab']`, or shift+tab (but `ev.key` would still be 'tab').
    
    @TODO - implement arrow key functionality and also shift-tabbing
    """
    
    # special case: tab and shift-tab:
    # list-ize the set, then just move to the next
    if key_ev.name == 'KEY_TAB':
        ordered_hoverable_elements = list(hoverable_elements)
        # Logger.log(f"[Get Next Hoverable]: {ordered_hoverable_elements=}")
        curr_index = ordered_hoverable_elements.index(currently_hovered) if currently_hovered is not None else -1
        next_index = (curr_index + 1) % len(ordered_hoverable_elements)
            
        return ordered_hoverable_elements[next_index]
    
    elif key_ev.name in ['KEY_UP', 'KEY_DOWN', 'KEY_LEFT', 'KEY_RIGHT', 'KEY_TAB']:
        # return random element in hoverable_elements. This is a placeholder. Then, add it back
        # TODO

        if len(hoverable_elements) == 0: return

        selected = hoverable_elements.pop()
        hoverable_elements.add(selected)
        return selected
    else:
        raise ValueError(f"Invalid key event for selecting elements: {key_ev.key}.")
    # note: all this stuff will be removed when the algorithm for selecting is actually implemented.

def len_no_ansi(string: str) -> str:
    """
    @see - https://github.com/chalk/ansi-regex/blob/0755e661553387cfebcb62378181e9f55b2567ff/index.js
    """
    return len(re.sub(
        r'[\u001B\u009B][\[\]()#;?]*((([a-zA-Z\d]*(;[-a-zA-Z\d\/#&.:=?%@~_]*)*)?\u0007)|((\d{1,4}(?:;\d{0,4})*)?[\dA-PR-TZcf-ntqry=><~]))', '', string))

def remove_ansi(string: str) -> str:
    """
    Removes color/style codes from a string.
    
    @see - https://github.com/chalk/ansi-regex/blob/0755e661553387cfebcb62378181e9f55b2567ff/index.js
    """
    return re.sub(
        r'[\u001B\u009B][\[\]()#;?]*((([a-zA-Z\d]*(;[-a-zA-Z\d\/#&.:=?%@~_]*)*)?\u0007)|((\d{1,4}(?:;\d{0,4})*)?[\dA-PR-TZcf-ntqry=><~]))', '', string)

def indexof_first_larger_than(nums: list, target: int | float) -> int:
    """
    IMPORTANT: uses binary search, so nums should be sorted in ascending order.
    
    Returns the index of the first element in `nums` that is larger than `target`.
    If target is larger than all elements, returns len(nums).
    """
    left = 0
    right = len(nums)
    
    while left < right:
        mid = (left + right) // 2
        
        if nums[mid] <= target:
            left = mid + 1
        else:
            right = mid
    
    return left

if os.name == 'nt':
    import msvcrt
    import ctypes

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]

def hide_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()