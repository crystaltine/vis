from typing import Union, Tuple, TYPE_CHECKING, List
from logger import Logger
import re
import os
import numpy as np
from skimage.draw import line, disk
from gd_constants import GDConstants
from draw_utils import print3

if TYPE_CHECKING:
    from render.constants import CameraConstants


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

def mix_colors_opt(color1: tuple, color2: tuple, amount: float) -> tuple:
    """
    ### Important: does not handle alpha values, that should be passed in as "amount".
    
    Optimized ver of mix_colors (rgb (no alpha) tuple only), with amount being a float from 0 to 1: 0 is closest to color1, 1 is closest to color2.
    Returns a rgb tuple (no alpha)
    
    Input format: 3-tuple of rgb values, 0-255.
    """
        
    # mix colors
    return tuple(int(color1[i] + (color2[i] - color1[i]) * amount) for i in range(3))

def combine_alpha(dest_alpha: int, new_alpha: int) -> int:
    """
    dest_alpha: alpha of the pixel being drawn on
    new_alpha: alpha of the color being applied to that pixel
    """
    
    return int(dest_alpha + new_alpha * (1 - dest_alpha / 255))

def blend_pixels(original: tuple | np.ndarray, new: tuple | np.ndarray) -> tuple | np.ndarray:
    """
    Function to truly blend pixels, including their alpha values.
    Inputs: 2 4-tuples of RGBA, returns a 4-tuple of RGBA.
    dest is the color that was already there, new is the color being applied. 
    """
    
    #Logger.log(f"attempting to blend {dest} with new={new}")
    if new[3] == 0:
        return original # if new is transparent, don't blend at all (also fixes divide by zero error later on)

    dest_rgb = original[:3]
    dest_alpha = original[3]
    
    new_rgb = new[:3]
    new_alpha = new[3]
    
    # calculate the new alpha
    alpha = combine_alpha(dest_alpha, new_alpha)
    
    # calculate the new rgb
    rgb = tuple(int((new_rgb[i]*new_alpha + dest_rgb[i]*dest_alpha*(1 - new_alpha/255)) / alpha) for i in range(3))
    
    Logger.log(f"[blend_pixels] blended {original} with {new} to get {rgb + (alpha,)}")
    return rgb + (alpha,)

def blend_rgba_onto_rgb(original: np.ndarray, new: np.ndarray) -> np.ndarray:
    """
    Blends a pixel (with transparency) onto a non-transparent pixel.
    A 4-tuple is expected for the new pixel (no 3-tuples).
    """

    new_rgb = new[:3]
    new_alpha = new[3] / 255
    
    return np.array([
        int(new_rgb[i]*new_alpha + original[i]*(1 - new_alpha)) for i in range(3)
    ])
    
def blend_rgba_img_onto_rgb_img(original: np.ndarray, new: np.ndarray) -> np.ndarray:
    """
    Blends two entire 2D arrays of pixels (so, techincally, 3D arrays) together, expecting
    that the original image is fully opaque and the new image has transparency. If the new
    image is RGB-based (no alpha, 3 channels), it will be treated as fully opaque.
    
    Will clip the new image to the size of the original image, anchoring the top left corner.
    """
    
    # if the new image has no alpha, just return the new image
    if new.shape[2] == 3:
        return new
    
    clipped_new = new[:original.shape[0], :original.shape[1]]
    
    # if new image has 0 in any shape, return
    if clipped_new.shape[0] == 0 or clipped_new.shape[1] == 0:
        return original

    new_rgb = clipped_new[..., :3] # "img" without alpha
    new_alpha = clipped_new[..., 3] / 255.0 # array of just the alpha values
    # blend arrays in PARALLEL (yayyyyyyyy!!!!) 
    #Logger.log(f"blend rgba into rgb: shapes of original, new: {original.shape}, {new.shape}")
    blended_rgb = new_rgb*new_alpha[..., np.newaxis] + original*(1 - new_alpha[..., np.newaxis])

    # return as uint8 types since this returns floats
    return blended_rgb.astype(np.uint8)

def blend_rgba_img_onto_rgb_img_inplace(original: np.ndarray, new: np.ndarray) -> None:
    """ Same as `blend_rgba_img_onto_rgb_img`, but modifies the original array in place. """
    original[:] = blend_rgba_img_onto_rgb_img(original, new)

def draw_line(image: np.ndarray, pos1: tuple, pos2: tuple, color: "CameraConstants.RGCameraBTuple", width: int = 1) -> None:
    """
    draw a fully opaque line of color `color` on the image from pos1= (x1, y1) to pos2= (x2, y2).
    modifies `image` in place, does not return anything.
    """
    
    x1, y1 = pos1
    x2, y2 = pos2
    
    # Get the coordinates of the line
    rr, cc = line(y1, x1, y2, x2)

    # Clip the coordinates to be within the image dimensions
    rr_clipped = np.clip(rr, 0, image.shape[0]-1)
    cc_clipped = np.clip(cc, 0, image.shape[1]-1)
    
    # for all the rrs that were clipped off, remove the corresponding ccs, otherwise it creates a flat line at the edge
    rr_diffs = rr - rr_clipped
    cc_clipped = cc_clipped[rr_diffs == 0]
    
    #cc_diffs = cc - cc_clipped
    #rr_clipped = rr_clipped[cc_diffs == 0]

    for r, c in zip(rr, cc):
        rr_disk, cc_disk = disk((r, c), radius=width)
        
        # Clip the coordinates to be within the image dimensions
        rr_disk = np.clip(rr_disk, 0, image.shape[0] - 1)
        cc_disk = np.clip(cc_disk, 0, image.shape[1] - 1)
        
        image[rr_disk, cc_disk] = color
    

def blend_multiple_pixels(dstacked_pixels: np.ndarray) -> tuple | np.ndarray:
    """
    Blends multiple pixels together. 
    Pixels should be in order of how they should be blended.
    """
    
    Logger.log(f"blend_multiple_pixels: dstacked_pxs shape is {dstacked_pixels.shape}")
    num_pixels = dstacked_pixels.shape[0] // 4
    Logger.log(f"blending {num_pixels} pixels")
    Logger.log(f"pixels: {dstacked_pixels}")
    

    blended = blend_pixels(dstacked_pixels[:4], dstacked_pixels[4:8])
    
    for i in range(2, num_pixels):
        blended = blend_pixels(blended, dstacked_pixels[i*4:i*4+4])
        
    return blended

def cls():
    """
    Clears the terminal using 'cls'

    @TODO - uh i forgot how to check for OS names, idk if cls works everywhere. works on ps win11 tho.
    """
    os.system('cls')

def draw_text(text:str, x:int, y:int, bold=False, underline=False, color: str | tuple = "#ffffff", bg_color: str | tuple = None):
    line=GDConstants.term.move_xy(x, y)
    if bold:
        line+=GDConstants.term.bold
    if underline:
        line+=GDConstants.term.underline
    
    line += fcode(color, bg_color) + text + GDConstants.term.normal
    print3(line)

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

def first_diff_color(arr1: np.ndarray, arr2: np.ndarray) -> int | None:
    """
    Returns the index of the first different color in the two arrays. If exactly the same, returns None.
    Both arrays must be 2d numpy arrays, with the 2d axis being 4 long (r,g,b,a)
    
    For example:
    
    `first_diff_color([[1, 2], [3, 6], [4, 200]], [[1, 2], [3, 9], [4, 202]]) -> 1`
    (both i=2 and i=3 are different, but returns 1 since the second pixel is the first different one)
    """
    differences = np.any(arr1 != arr2, axis=1)
    #Logger.log(f"first diff: arr1 first 10 elements: {arr1[:10]}, arr2 first 10 elements: {arr2[:10]}" )
    first_diff = np.argmax(differences)
    
    # if flat index is 0, investigate: it could be that all are the same, or that the first element is actually different
    if first_diff == 0 and not differences[0]:
        return None
    
    return first_diff

def last_diff_color(arr1: np.ndarray, arr2: np.ndarray) -> int | None:
    """
    Returns the index of the last different color in the two arrays. If exactly the same, returns None.
    Both arrays must be 2d numpy arrays, with the 2d axis being 4 long (r,g,b,a)
    
    For example:
    
    `last_diff_color([[1, 2], [3, 6], [4, 200]], [[1, 9], [3, 9], [4, 200]]) -> 1`
    (both i=0 and i=1 are different, but returns 1 since the second pixel is the last different one)
    """
    differences = np.any(arr1 != arr2, axis=1)
    last_diff = len(differences) - np.argmax(differences[::-1]) - 1
    
    # if flat index is last, investigate: it could be that all are the same, or that the first element is actually different
    if last_diff == len(differences) - 1 and not differences[-1]:
        return None
    
    return last_diff

def lesser(a: int | None, b: int | None) -> int | None:
    """
    Takes two numbers that are either None or an int.
    
    If both are not None, then returns the lesser of the two
    If one of them is None, returns the one that isn't None
    If both are None, returns None
    """
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)

def greater(a: int | None, b: int | None) -> int | None:
    """
    Takes two numbers that are either None or an int.
    
    If both are not None, then returns the greater of the two
    If one of them is None, returns the one that isn't None
    If both are None, returns None
    """
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b)

def get_diff_intervals(arr1: np.ndarray, arr2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Given two 1D np arrays of THE SAME LENGTH, return a tuple
    of ndarrays (starts, ends) that represent the intervals on which the original arrays are different.

    (the intervals are go from start -> end-1, inclusive.)
    """

    diffs = np.any(arr1 != arr2, axis=1).astype(int)
    
    changes = np.diff(diffs, prepend=0, append=0)
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]
    
    return starts, ends

def combine_intervals(starts1: np.ndarray, ends1: np.ndarray, starts2: np.ndarray, ends2: np.ndarray) -> List[Tuple[int, int]]:
    """ Combines arbitrary intervals defined by starts1, ends1, and starts2, 
    ends2 into one giant LIST of intervals (tuple (start, end), exclusive of end).
    Could technically be optimized 
    """
    intervals = []
    
    starts1 = add_row_of(starts1, 1) # 1st ele being 1 means its a start
    starts2 = add_row_of(starts2, 1)
    ends1 = add_row_of(ends1, -1) # 2nd ele being -1 means its an end
    ends2 = add_row_of(ends2, -1) 
    
    combined = np.vstack((starts1, starts2, ends1, ends2)).tolist()
    combined.sort(key=lambda x: x[0])
    
    intervals = []
    excess_starts = 0
    curr_start_index = 0
    for i in range(len(combined)):
        excess_starts += combined[i][1] # +1 for starts, -1 for ends
        
        if excess_starts == 0:
            intervals.append((combined[curr_start_index][0], combined[i][0]))
            curr_start_index = i+1
            
    return intervals    

def add_row_of(arr: np.ndarray, num: int) -> np.ndarray:
    """ For a 1D array arr, "enumerates" the array (similar to python's enumerate func) 
    by adding another row filled with `num` underneath the original list. """
    result = np.vstack((arr, np.full_like(arr, num)))
    return result.transpose()

def distances_to_false(bool_array: np.ndarray) -> np.ndarray:
    """
    Given a 1D array of booleans, returns a 1D array of integers representing the distances between
    consecutive False values. If there are no False values, returns an empty array.
    """
    # Find the indices where the array is False
    false_indices = np.where(bool_array)[0]
    
    # Calculate the distances between consecutive False indices
    if len(false_indices) == 0:
        return np.array([])  # Return an empty list if there are no False values

    # Distances between consecutive Falses
    distances = np.diff(false_indices) - 1

    # Include distance from the start to the first False if it starts with True
    if false_indices[0] != 0:
        distances = np.insert(distances, 0, false_indices[0])

    return distances

def get_false_chunk_sizes(bool_array: np.ndarray) -> np.ndarray:
    """ Given a 1D boolean np array, returns a 1D np array of ints that contains the lengths
    of the consecutive false intervals. Does not include any 0-length intervals (skips through true chunks). """

    if len(bool_array) == 0:
        return np.array([])

    diffs = np.diff(bool_array)
    changes = np.where(diffs == True)[0] + 1

    # edge cases - count chunks at start or end of input
    if bool_array[0] == False:
        changes = np.insert(changes, 0, 0)
    if bool_array[-1] == False:
        changes = np.append(changes, len(bool_array))


    # every even index is the start of a false chunk
    # every odd index is the end of a false chunk (exclusive)
    # return odd - even elements (those are the sizes)
    return changes[1::2] - changes[::2]