from globalvars import Globals
from utils import convert_to_chars, fcode

f=fcode
""" alias """

logo_1 = [
    "   ▄▀      ▀▄   ",
    "  █▀  ▄█▀   ▀█  ",
    "▄█▀ ▄█ ▄ ▀█  ▀█▄",
    "▀█▄  █▄ ▀ █▀ ▄█▀",
    "  █▄   ▄█▀  ▄█  ",
    "   ▀▄      ▄▀   "
]
logo_spectral = [
    f'   {f("e4c2ff")}▄{f("ded2ff")}▀      {f("f8ab8f")}▀{f("f8bc8f")}▄   ',
    f'  {f("ffa9fd")}█{f("e4c2ff")}▀  {f("8ca7b5")}▄{f("4d5258")}█{f("373d43")}▀   {f("f8ca8f")}▀{f("ffddab")}█  ',
    f'{f("f66bf3")}▄{f("ff85fd")}█{f("fa98f7")}▀ {f("5f7c8b")}▄{f("bbd5e1")}█ {f("ffffff")}▄ {f("9ddefb")}▀{f("79aac0")}█  {f("fce2b7")}▀{f("fff1cc")}█{f("c3b060")}▄',
    f'{f("f188e1")}▀{f("ff94e4")}█{f("ff9dd4")}▄  {f("79aac0")}█{f("9ddefb")}▄ {f("ffffff")}▀ {f("bbd5e1")}█{f("5f7c8b")}▀ {f("f5eab5")}▄{f("c3b16c")}█{f("b09639")}▀',
    f'  {f("f4abd4")}█{f("fab7d4")}▄   {f("373d43")}▄{f("4d5258")}█{f("8ca7b5")}▀  {f("f5e598")}▄{f("bfac65")}█  ',
    f'   {f("f6c2d5")}▀{f("f6c2c8")}▄      {f("f5c86b")}▄{f("ffe784")}▀   '
]

# horizontal length is 16
# vertical length is 6

def plaster_logo(center_x: int | str, center_y: int | str):
    """
    Draw the temporary viscord logo on the screen.
    `center_x` is a dimvalue that represents the center x-coordinate of the logo.
    `center_y` is a dimvalue that represents the center y-coordinate of the logo.
    
    Dimvalues can be either measured in characters (e.g. '20ch') or percents (e.g. '50%').
    In this case, percentages are taken of the full screen.
    """
    
    # first, convert the dimvalues to characters
    center_x = convert_to_chars(Globals.__vis_document__.term.width, center_x)
    center_y = convert_to_chars(Globals.__vis_document__.term.height, center_y)
    
    # calculate the top left corner of the logo
    logo_top = center_y - 3
    logo_left = center_x - 8
    
    # draw the logo
    for i in range(6):
        print(f(background="111820"))
        print(Globals.__vis_document__.term.move_xy(logo_left, logo_top + i) + logo_spectral[i])