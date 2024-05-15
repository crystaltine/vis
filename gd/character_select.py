from draw_utils import draw_rect, cls, Position, convert_to_chars
from GD import GD
from logger import Logger
from img2term.main import draw
import traceback
from icons import draw_cube_icon, COLORS_1, COLORS_2

class CharacterSelect:
    """
    General class for handling the character selection screen, accessible from the main menu.
    """
    
    CUBE_ICON_SIZE = (4, 8) # rows, cols in each icon
    
    selected_cube = 0
    selected_primary_color = 0
    selected_secondary_color = 4
    
    def render():
        """
        Draws the character selection screen based on current terminal size, and classwide config options
        (such as if menus are open, which icons are currently selected, etc.)
        """
        cls()
        
        # bg
        draw_rect("#c2c2c2", Position.Relative(0, 0, 0, 0))
        
        CharacterSelect._draw_title()       
        CharacterSelect._draw_color_selector()
        CharacterSelect._draw_panel_bgs()
        CharacterSelect._draw_cube_list()
        CharacterSelect._draw_color_list()
        CharacterSelect._draw_currently_selected_cube()
        
    def _draw_title():
        """ Helper func for drawing the top title bar, including rendering font """
        draw_rect("#e8e8e8", Position.Relative(left=0, right=0, top=0), height="20%")
        
        # IMPORTANT - this image is 100ch x 6ch.
        draw("assets/character_select/character_select_title.png", pos=Position.Relative(top="calc(10% - 3ch)", left="calc(50% - 50ch)"))
        
    def _draw_color_selector():
        """ Helper func for drawing the color selector at bottom of screen """
        # TODO - for now only draws bg
        draw_rect("#838383", Position.Relative(left=0, right=0, bottom=0), height="30%")

    def _draw_panel_bgs():
        """ draws bg panels for the selected icon display and the list of icons """
        # NOTE: for these numbers, see assets/character_select/character_select_screen_calcs.png
        draw_rect("#767676", Position.Relative(left="calc(42% - 65ch)", top="calc(45% - 8ch)"), height=16, width=32)
        draw_rect("#767676", Position.Relative(right="calc(42% - 69ch)", top="calc(45% - 9ch)"), height=18, width=114)

    def _draw_cube_list():
        """ Draws the (hardcoded) 30 cube icons available for selection. 10 per row, 2px gap between icons. """
        # either add scrolling or hardcode only 30 cube icons in. (probably the latter lol)
        
        # NOTE: for these numbers, see assets/character_select/character_select_screen_calcs.png
        # top/left of first icon is at t=45% - 7ch, l=58% - 37ch
        # increment by 10ch between icons and 5ch between rows
        # TODO - tint these some other color rather than black and white?
        
        # tests
        #a = Position.Relative(left="calc(58% - 37ch)", top="calc(45% - 7ch)")
        #Logger.log(f"abs pos of first icon: {a.get_absolute()}")
        
        # draw 3 rows
        for row in range(3):
            for col in range(10):
                draw_cube_icon(row*10+col, Position.Relative(left=f"calc(58% - {37-col*10}ch)", top=f"calc(45% - {7-row*5}ch)"))

    def _draw_color_list():
        """
        Draws the (hardcoded) 32 colors available for selection. 10ch x 5ch, 16 per row, 2px gap between squares.
        """
        # NOTE: for these numbers, see assets/character_select/character_select_screen_calcs.png
        
        # the first color in COLORS_2 should be rendered at bottom=(30% - (0.09*term.width))/2, left=8.5%
        # b = 15% - (0.09*term.width/2)ch
        # from then on, each next color square is 5% to the right (13.5%, then 18.5%, etc.)
        # COLORS_1 is the exact same but bottom=(20% - (0.09*term.width))/2 + 5%
        Logger.log(f"color rects have height of {convert_to_chars(GD.term.width, '4%')}")
        for i in range(16):
            draw_rect(COLORS_2[i], Position.Relative(left=f"{8.5+5*i}%", bottom=f"calc(15% - {round(0.045*GD.term.width/2)}ch)"), width="4%", height=convert_to_chars(GD.term.width, "2%"))
            draw_rect(COLORS_1[i], Position.Relative(left=f"{8.5+5*i}%", bottom=f"calc(15% + {round(0.005*GD.term.width/2)}ch)"), width="4%", height=convert_to_chars(GD.term.width, "2%"))

    def _draw_currently_selected_cube():
        """ Draws an enlarged rendering of the currently selected cube icon """
        # TODO - currently does not tint the icon - it stays black and white
        
        # NOTE: for these numbers, see assets/character_select/character_select_screen_calcs.png
        draw_cube_icon(CharacterSelect.selected_cube, Position.Relative(left="calc(42% - 57ch)", top="calc(45% - 4ch)"), scale=4)

# testing
try:
    CharacterSelect.render()
except Exception as e:
    Logger.log(f"Error in CharacterSelect.render(): {e}")
    Logger.log(f"Traceback: {traceback.format_exc()}")
    print(f"\x1b[31m{traceback.format_exc()}\x1b[0m")
    
Logger.write()