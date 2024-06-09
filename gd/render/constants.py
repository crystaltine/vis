import blessed
from render.utils import nearest_quarter
from typing import Tuple
from enum import Enum
from gd_constants import GDConstants

class CameraConstants:
    BLOCK_WIDTH = 8
    """ How wide a block is in pixels (half of a character: ▀) """
    BLOCK_HEIGHT = 8
    """ How tall a block is in pixels (half of a character: ▀) """

    CAMERA_LEFT_OFFSET = int(GDConstants.term.width * 0.3 / BLOCK_WIDTH)
    """ Amount of BLOCKS the camera_left is behind the player x position """

    MIN_PLAYER_SCREEN_OFFSET = 0.25
    """ The minimum proportion of the screen height the player should be from the top of the screen, at all times.
    For example, if =0.25, then the player should never be rendered in the top 25% of the screen - the camera would move up instead. """

    MAX_PLAYER_SCREEN_OFFSET = 0.75
    """ The maximum proportion of the screen height the player should be from the top of the screen, at all times.
    For example, if =0.75, then the player should never be rendered in the bottom 25% of the screen - the camera would move down instead. """

    GROUND_HEIGHT = 3
    """ Max height of the ground in BLOCKS. This determines how much the rest of the level is "pushed up" """
    
    # for renderer only - physics runs at ~240
    # also, this is a target rate only.
    # I've tested, it still runs at ~30fps.
    RENDER_FRAMERATE = 90 
    """ Framerate of the renderer. In practice, works a bit wonky, =60 brings 1000FPS down to ~40 ish, probably because windows clock isnt super accurate. """

    class OBJECT_ROTATIONS(Enum):
        UP = "up"
        DOWN = "down"
        LEFT = "left"
        RIGHT = "right"
        
    class OBJECT_REFLECTIONS(Enum): 
        NONE = "none"
        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"
        BOTH = "both"
        
    ROTATIONS_CLOCKWISE = {
        "up": "right",
        "right": "down",
        "down": "left",
        "left": "up"
    }
    ROTATIONS_COUNTERCLOCKWISE = {
        "up": "left",
        "right": "up",
        "down": "right",
        "left": "down"
    }

    REFLECTIONS_HORIZONTAL = {
        "none": "horizontal",
        "horizontal": "none",
        "vertical": "both",
        "both": "vertical"
    }
    REFLECTIONS_VERTICAL = {
        "none": "vertical",
        "horizontal": "both",
        "vertical": "none",
        "both": "horizontal"
    }
    REFLECTIONS_BOTH = {
        "none": "both",
        "horizontal": "vertical",
        "vertical": "horizontal",
        "both": "none"
    }
        
    RGBTuple = Tuple[int, int, int]
    RGBATuple = Tuple[int, int, int, int]

    def screen_width_blocks(term: blessed.Terminal) -> float:
        """
        Returns the width of the screen in BLOCKS. does NOT round.
        See `CameraConstants.BLOCK_WIDTH` for pixel width of each block.
        """

        return term.width / CameraConstants.BLOCK_WIDTH

    def screen_height_blocks(term: blessed.Terminal) -> float:
        """
        Returns the height of the screen in BLOCKS. Does NOT round.
        See `CameraConstants.BLOCK_HEIGHT` for character width of each block.
        """

        return term.height*2 / CameraConstants.BLOCK_HEIGHT
    
    def get_screen_x(camera_left: int, x: float) -> int:
        """ Returns the screen x-coordinate (relative to left of frame) 
        of a given grid position based on a given camera position. """
        
        return round((x - camera_left) * CameraConstants.BLOCK_WIDTH)
    
    def get_screen_y(camera_bottom: int, camera_height: int, y: float) -> int:
        """ Returns the screen y-coordinate (relative to bottom of frame) 
        of a given grid position based on a given camera position. """
        
        return camera_height - round((1 + y - camera_bottom) * CameraConstants.BLOCK_HEIGHT)

    def get_screen_coordinates(camera_left: int, camera_bottom: int, camera_height: int, x: float, y: float) -> Tuple[int, int]:
        """ Returns the screen coordinates (relative to top left of camera) of the TOP LEFT corner
        of a given grid position based on a given camera position. """
        
        return (
            CameraConstants.get_screen_x(camera_left, x),
            CameraConstants.get_screen_y(camera_bottom, camera_height, y)
        )
    
    def center_screen_coordinates(term: blessed.Terminal) -> list:
        """
        Returns the coordinates of the center of the screen in BLOCKS.
        """

        return [term.width//(CameraConstants.BLOCK_WIDTH*2), term.height//(CameraConstants.BLOCK_HEIGHT*2)]
    
    def grid_to_terminal_pos(gridx: float, gridy: float) -> tuple:
        """
        Converts a camera grid position (block) to the TOP LEFT CORNER of
        its equivalent pixel position. (0, 0) -> (0, 0) (top left corner of screen)
        
        For example, (0, 0) should go to (0, 0)

        Assuming one block is 4 chars wide by 4 chars tall, 
        (1, 1) would map to (4, 4).
        
        This also supports decimals.
        For example:
        - (0.1, 0.45) -> (0, 2)

        The output of this function is determined by
        `CameraConstants.BLOCK_WIDTH` and `CameraConstants.BLOCK_HEIGHT`.

        Returns tuple (x, y) of ints.
        """

        return (
            round(nearest_quarter(gridx) * CameraConstants.BLOCK_WIDTH),
            round(nearest_quarter(gridy) * CameraConstants.BLOCK_HEIGHT)
        )
        