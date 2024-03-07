import blessed
from render.utils import nearest_quarter

class CameraUtils:
    GRID_PX_X = 4 # how wide a block is in characters
    GRID_PX_Y = 2 # how tall a block is in characters

    CAMERA_LEFT_OFFSET = 10 # amount of blocks the camera_left is behind the player x

    DEFAULT_GROUND_TOP_PERCENT = 70 # in BLOCKS
    
    # for renderer only - physics runs at ~240
    # also, this is a target rate only.
    # I've tested, it still runs at ~30fps.
    RENDER_FRAMERATE = 60 
    

    def screen_width_blocks(term: blessed.Terminal) -> int:
        """
        Returns the width of the screen in BLOCKS. Floors to next highest int.
        See `CameraUtils.GRID_PX_X` for character width of each block.
        """

        return term.width // CameraUtils.GRID_PX_X

    def screen_height_blocks(term: blessed.Terminal) -> int:
        """
        Returns the height of the screen in BLOCKS. Floors to next highest int.
        See `CameraUtils.GRID_PX_Y` for character width of each block.
        """

        return term.height // CameraUtils.GRID_PX_Y

    def grid_to_terminal_pos(gridx: float, gridy: float) -> tuple:
        """
        Converts a camera grid position (block) to the TOP LEFT CORNER of
        the character-based position on the terminal. All zero-indexed ((0,0) is top left)
        
        For example, (0, 0) should go to (0, 0)

        Assuming one block is 4 chars wide by 2 chars tall, 
        (1, 1) would map to (4, 2).
        
        This also supports decimals. We round to nearest quarter.
        For example:
        - (0.1, 0.45) -> (0, 2)

        The output of this function is determined by
        `CameraUtils.GRID_PX_X` and `CameraUtils.GRID_PX_Y`.

        Returns tuple (x, y) of ints.
        """

        return (
            round(nearest_quarter(gridx) * CameraUtils.GRID_PX_X),
            round(nearest_quarter(gridy) * CameraUtils.GRID_PX_Y)
        )