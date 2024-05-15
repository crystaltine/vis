from img2term.main import draw_from_pixel_array
from PIL import Image
from draw_utils import Position

COLORS_1 = [
    '#18e700', '#4dffc0', '#4dfdff', '#ffffff', '#a7a7a7', '#4e4e4e', '#000000',
    '#010078', '#0015e5', '#1a66ff', '#07a4ff', '#460075', '#5d0b00', '#545d00', '#004902'
]
COLORS_2 = [
    '#ffab00', '#ffe800', '#fdffa1', '#feffdb', '#ff1900', '#ff005c', '#ff00b0', '#c242d4',
    '#ffb6d5', '#afe5ef', '#afefb2', '#c2caff', '#446786', '#86446d', '#618644', '#675b21'
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