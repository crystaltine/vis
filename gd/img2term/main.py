import blessed
import numpy
from PIL import Image
from img2term.utils import fcode, fcode_opt, cls
from typing import List, Tuple, Literal
from logger import Logger

term = blessed.Terminal()

PIXEL = "▀" # top half is bg, bottom half is fg
print_v = numpy.vectorize(print)

def draw(
    img_path: str, 
    topleft_pos: Tuple[int, int] = (0, 0), 
    maxsize: Tuple[int, int] = (None, None), 
    overflow_behavior: Literal['crop', 'scale'] = 'crop') -> None:
    """
    Prints an image to the current terminal window.

    `img_path` path to image file, relative to the current working directory.
    
    `topleft_pos` tuple of (x, y) of where the top left corner of the image will be printed. 
    x is column, y is row. default is (0, 0).
    
    `maxsize` tuple of (width, height) of the maximum size of the image to be printed. Dimensions
    that are smaller than this won't be affected. maxsize of None means no limit. default is (None, None).
    
    `overflow_behavior` string that determines how the image will be handled if it is larger than
    `maxsize`. If 'crop', the image will be cropped to fit the dimensions. If 'scale', the image
    will be scaled down to fit the dimensions. default is 'crop'.
    """
    im = Image.open(img_path)
    width, height = im.size
    
    # do any resizing if necessary
    if overflow_behavior == 'scale':
        im = im.resize((
            min(maxsize[0], width) if maxsize[0] is not None else width,
            min(maxsize[1], height) if maxsize[1] is not None else height
        ))    
    elif overflow_behavior == 'crop':
        im = im.crop((
            0, 0, 
            min(maxsize[0], width) if maxsize[0] is not None else width,
            min(maxsize[1], height) if maxsize[1] is not None else height
        ))
    else:
        raise ValueError("[img2term] invalid arg in draw(): overflow_behavior must be 'crop' or 'scale'")

    pixels = numpy.array(im, dtype=numpy.uint8)
    
    final_chars: List[List[str]] = []
    for i in range(0, len(pixels)-1, 2): # TODO - last row of odd height images is not being processed
        row = pixels[i]
        row2 = pixels[i + 1]
        
        final_row: List[str] = []
        
        for j in range(len(row)):
            top_pixel = row[j]
            bottom_pixel = row2[j]
            final_row.append("\x1b[0m" + fcode_opt(fg=top_pixel[0:3], bg=bottom_pixel[0:3]) + PIXEL)
            
        final_chars.append(final_row)
    
    final_chars = numpy.array(final_chars)
    
    # draw image at specified pos
    for row in range(len(final_chars)):
        print(term.move_xy(topleft_pos[0], topleft_pos[1]+row) + ''.join(final_chars[row]) + '\x1b[0m')
    
# demo i guess
# draw("demo.png", topleft_pos=(0, 0), maxsize=(200, 100), overflow_behavior="crop")