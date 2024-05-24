import blessed
from render.utils import nearest_quarter

class CameraUtils:
    GRID_CELL_WIDTH = 4 
    """ How wide a block is in pixels (half of a character: ▀) """
    GRID_CELL_HEIGHT = 4 
    """ How tall a block is in pixels (half of a character: ▀) """

    CAMERA_LEFT_OFFSET = 10
    """ Amount of BLOCKS the camera_left is behind the player x position """

    # TODO -rework how ground is displayed
    DEFAULT_GROUND_TOP_PERCENT = 70 # in BLOCKS
    
    # for renderer only - physics runs at ~240
    # also, this is a target rate only.
    # I've tested, it still runs at ~30fps.
    RENDER_FRAMERATE = 60 

    def screen_width_blocks(term: blessed.Terminal) -> int:
        """
        Returns the width of the screen in BLOCKS. rounds down
        See `CameraUtils.GRID_CELL_WIDTH` for pixel width of each block.
        """

        return term.width // CameraUtils.GRID_CELL_WIDTH

    def screen_height_blocks(term: blessed.Terminal) -> int:
        """
        Returns the height of the screen in BLOCKS. Floors to next highest int.
        See `CameraUtils.GRID_CELL_HEIGHT` for character width of each block.
        """

        return term.height // CameraUtils.GRID_CELL_HEIGHT
    
    def center_screen_coordinates(term: blessed.Terminal) -> list:
        """
        Returns the coordinates of the center of the screen in BLOCKS.
        """

        return [term.width//(CameraUtils.GRID_CELL_WIDTH*2), term.height//(CameraUtils.GRID_CELL_HEIGHT*2)]
    
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
        `CameraUtils.GRID_CELL_WIDTH` and `CameraUtils.GRID_CELL_HEIGHT`.

        Returns tuple (x, y) of ints.
        """

        return (
            round(nearest_quarter(gridx) * CameraUtils.GRID_CELL_WIDTH),
            round(nearest_quarter(gridy) * CameraUtils.GRID_CELL_HEIGHT)
        )