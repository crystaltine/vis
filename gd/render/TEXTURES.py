from render.utils import fcode

class TEXTURES:
    
    BG_COLOR = "#287DFF"
    GROUND_COLOR = "#0046cf"
    BLOCK_COLOR_1 = "#444"
    BLOCK_COLOR_2 = "#555"
    
    YELLOW_ORB_COLOR = "#fe0"
    PURPLE_ORB_COLOR = "#e0f"
    BLUE_ORB_COLOR = "#0ff"
    
    PLAYER_ICON = [
        fcode("00f", "ff0")+"o  o",
        fcode("00f", "ff0")+"====",
    ]
    
    spike = [
        f"{fcode(background=BG_COLOR)} {fcode(foreground='000')}/\\{fcode(background=BG_COLOR)} ",
        f"{fcode(foreground='000')}/__\\"
    ]
    block = [
        f"{fcode(background=BLOCK_COLOR_1)}    ",
        f"{fcode(background=BLOCK_COLOR_2)}    "
    ]
    yellow_orb = [
        f'{fcode(background="fff")} {fcode(background=YELLOW_ORB_COLOR)}  {fcode(background="fff")} ',
        f'{fcode(background="fff")} {fcode(background=YELLOW_ORB_COLOR)}  {fcode(background="fff")} ',
    ]
    purple_orb = [
        f'{fcode(background="fff")} {fcode(background=PURPLE_ORB_COLOR)}  {fcode(background="fff")} ',
        f'{fcode(background="fff")} {fcode(background=PURPLE_ORB_COLOR)}  {fcode(background="fff")} ',
    ]
    blue_orb = [
        f'{fcode(background="fff")} {fcode(background=BLUE_ORB_COLOR)}  {fcode(background="fff")} ',
        f'{fcode(background="fff")} {fcode(background=BLUE_ORB_COLOR)}  {fcode(background="fff")} ',
    ]
    
    def get(texture_name: str):
        return getattr(TEXTURES, texture_name)