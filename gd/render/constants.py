import blessed

class CameraUtils:
    GRID_PX_X = 4 # how wide a block is in characters
    GRID_PX_Y = 2 # how tall a block is in characters

    CAMERA_LEFT_OFFSET = 10 # amount of blocks the camera_left is behind the player x

    DEFAULT_GROUND_LEVEL_TOP = 70 # percent from top the ground will be located at

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

    def grid_to_terminal_pos(gridx: int, gridy: int) -> tuple:
        """
        Converts a camera grid position (block) to the TOP LEFT CORNER of
        the character-based position on the terminal. All zero-indexed ((0,0) is top left)
        
        For example, (0, 0) should go to (0, 0)

        Assuming one block is 4 chars wide by 2 chars tall, 
        (1, 1) would map to (4, 2).

        The output of this function is determined by
        `CameraUtils.GRID_PX_X` and `CameraUtils.GRID_PX_Y`.

        Returns tuple (x, y)
        """

        return gridx*CameraUtils.GRID_PX_X, gridy*CameraUtils.GRID_PX_Y
