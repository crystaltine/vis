class CONSTANTS:
    BLOCKS_PER_SECOND = 5
    GRAVITY = 5
    TERMINAL_VEL = 10

    PLAYER_HITBOX_X = 1
    PLAYER_HITBOX_Y = 1

    SOLID_SURFACE_LENIENCY = 0.2

    TARGET_FRAMERATE = 30

class SPEEDS:
    slow = 0.8
    normal = 1
    double = 1.4
    triple = 1.7
    quadruple = 2

    def decode(speedname):
        """
        Get the value of the speed name.
        Currently supported speeds (case sensitive):
        - slow (0.8)
        - normal (1)
        - double (1.4)
        - triple (1.7)
        - quadruple (2)

        For example, `SPEEDS.decode("slow") -> 0.8`

        Returns `None` if not found. 
        """
        return SPEEDS.__dict__.get(speedname)