from img2term.main import draw_from_pixel_array
from PIL import Image
from draw_utils import Position, colorize_pixel, hex_to_rgb

COLORS = [
    '#18e700', '#4dffc0', '#4dfdff', '#ffab00', '#ffe800', '#fdffa1', '#ffffff', '#a7a7a7', 
    '#4e4e4e', '#000000', '#010078', '#0015e5', '#07a4ff', '#ff1900', '#f1319a', '#c242d4',
]

def draw_cube_icon(icon_index: int, pos: Position.Relative, scale: int = 2) -> None:
    """
    Draws an icon at the specified position. For now these icons are 4ch wide x 2ch tall (4x4 pixels)
    Index corresponds to its order on the icon spritesheet. For example, the leftmost is 0, then 1, etc.
    """
    
    # load the spritesheet, but we only care about pixels in the 4x4 grid with
    # left=icon_index*4, top=0, right=icon_index*4+4, bottom=4
    # get pixels, then use draw_from_pixel_array to draw it

    sheet = Image.open("assets/character_select/spritesheet_cubes.png")
    
    pixels = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(sheet.getpixel((icon_index*4+j, i)))
        pixels.append(row)
        
    # expand pixels to scale
    pixels = [[px for px in row for _ in range(scale)] for row in pixels for _ in range(scale)]
        
    draw_from_pixel_array(pixels, pos)

def draw_colorized_cube_icon(icon_index: int, pos: Position.Relative, p_color: str | tuple, s_color: str | tuple, scale: int = 2) -> None:
    """
    Draws an icon at the specified position. For now these icons are 4ch wide x 2ch tall (4x4 pixels)
    
    p_color is primary color, s_color is secondary color. These are used to colorize the icon.
    
    Index corresponds to its order on the icon spritesheet. For example, the leftmost is 0, then 1, etc.
    """
    
    # load the spritesheet, but we only care about pixels in the 4x4 grid with
    # left=icon_index*4, top=0, right=icon_index*4+4, bottom=4
    # get pixels, then use draw_from_pixel_array to draw it

    sheet = Image.open("assets/character_select/spritesheet_cubes.png")
    
    rgbified_p_color = p_color if isinstance(p_color, tuple) else hex_to_rgb(p_color)
    rgbified_s_color = s_color if isinstance(s_color, tuple) else hex_to_rgb(s_color)
    
    pixels = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(sheet.getpixel((icon_index*4+j, i)))
        pixels.append(row)
        
    # expand pixels to scale
    pixels = [[colorize_pixel(px[0], rgbified_p_color, rgbified_s_color) for px in row for _ in range(scale)] for row in pixels for _ in range(scale)]
        
    draw_from_pixel_array(pixels, pos)

