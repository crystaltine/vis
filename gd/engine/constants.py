class CONSTANTS:
    BLOCKS_PER_SECOND = 9
    GRAVITY = 40
    TERMINAL_VEL = 20

    PLAYER_HITBOX_X = 1
    PLAYER_HITBOX_Y = 1
    
    PLAYER_JUMP_STRENGTH = 15
    """ How much the player's yvel is set to when they jump. """
    
    PURPLE_ORB_MULTIPLIER = 0.5
    
    BLUE_ORB_STARTING_VELOCITY = 3

    SOLID_SURFACE_LENIENCY = 0.2
    
    PHYSICS_FRAMERATE = 240
    
    QUIT_KEYS = ['q', 'ctrl+c']
    JUMP_KEYS = [' ', 'up', 'w']
    ALL_KEYS = set(QUIT_KEYS + JUMP_KEYS)

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