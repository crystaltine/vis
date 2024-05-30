class CONSTANTS:
    BLOCKS_PER_SECOND = 9
    GRAVITY = 50
    PLAYER_JUMP_STRENGTH = 16
    """ How much the player's yvel is set to when they jump. """
    TERMINAL_VEL = 30
    """ The maximum downward velocity the player can accumulate due to GRAVITY (can exceed if using a black orb, for example). """

    CUBE_GRAVITY_MULTIPLIER = 1
    BALL_GRAVITY_MULTIPLIER = 0.8
    UFO_GRAVITY_MULTIPLIER = 0.7

    PLAYER_HITBOX_X = 1
    PLAYER_HITBOX_Y = 1
    
    COOLDOWN_BETWEEN_ATTEMPTS = 0.5
    
    PURPLE_ORB_MULTIPLIER = 0.5
    
    BLUE_ORB_STARTING_VELOCITY = 3

    SOLID_SURFACE_LENIENCY = 0.2
    
    PHYSICS_FRAMERATE = 60
    
    QUIT_KEYS = ['q', 'ctrl+c']
    JUMP_KEYS = [' ', 'up', 'w']
    PAUSE_KEYS = ['p', '', 'esc']
    CHECKPOINT_KEYS = ['z']
    REMOVE_CHECKPOINT_KEYS = ['x']
    ALL_KEYS = set(QUIT_KEYS + JUMP_KEYS + PAUSE_KEYS + CHECKPOINT_KEYS + REMOVE_CHECKPOINT_KEYS)

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