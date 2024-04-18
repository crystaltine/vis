from render.utils import fcode

class TEXTURES:
    
    BG_COLOR = "#287DFF"
    GROUND_COLOR = "#0046cf"
    BLOCK_COLOR_1 = "#444"
    BLOCK_COLOR_2 = "#555"
    
    YELLOW_ORB_COLOR_1 = "#fe0"
    YELLOW_ORB_COLOR_2 = "#cb0"
    
    PURPLE_ORB_COLOR_1 = "#e0f"
    PURPLE_ORB_COLOR_2 = "#b0c"
    
    BLUE_ORB_COLOR_1 = "#0ff"
    BLUE_ORB_COLOR_2 = "#0cc"
    
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
        f'{fcode(background="fff")} {fcode(background=YELLOW_ORB_COLOR_1)}  {fcode(background="fff")} ',
        f'{fcode(background="fff")} {fcode(background=YELLOW_ORB_COLOR_2)}  {fcode(background="fff")} ',
    ]
    purple_orb = [
        f'{fcode(background="fff")} {fcode(background=PURPLE_ORB_COLOR_1)}  {fcode(background="fff")} ',
        f'{fcode(background="fff")} {fcode(background=PURPLE_ORB_COLOR_2)}  {fcode(background="fff")} ',
    ]
    blue_orb = [
        f'{fcode(background="fff")} {fcode(background=BLUE_ORB_COLOR_1)}  {fcode(background="fff")} ',
        f'{fcode(background="fff")} {fcode(background=BLUE_ORB_COLOR_2)}  {fcode(background="fff")} ',
    ]
    
    def get(texture_name: str):
        return getattr(TEXTURES, texture_name)