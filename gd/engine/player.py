from engine.constants import CONSTANTS, SPEEDS

class Player:
    """
    Represents the player inside a level and handles physics calculations.
    """

    def __init__(self, start_settings: dict = {}):
        """
        (OPTIONAL) `start_settings` format (mainly used for startpos):
        ```python
        {
            pos: [int, int], # [x, y] to start at, default [0, 0]
            speed: "slow", "normal", ... "quadruple" # see constants.SPEEDS
            gravity: int # set a starting gravity. CONSTANTS.gravity for default, negative that for reverse
        }
        ```

        If a setting isn't provided, default values are used,
        which will spawn a cube at [0,0] with regular speed and gravity.
        """
        self.speed = SPEEDS.decode(start_settings.get("speed")) or SPEEDS.normal
        self.pos = start_settings.get("pos") or [0, 0]
        """ [x, y], where x is horiz (progress) """

        self.yvel = 0
        self.gravity = start_settings.get("gravity") or CONSTANTS.GRAVITY

    def tick(self, timedelta: float):
        """ 
        Physics tick for the player.

        Timedelta should be in seconds and should represent the time since last tick.
        If this is the first tick, then timedelta should be 0 (i think).
        """
        self.pos[0] += self.speed * CONSTANTS.BLOCKS_PER_SECOND * timedelta
        self.pos[1] += self.yvel * timedelta
        self.yvel += self.gravity * timedelta