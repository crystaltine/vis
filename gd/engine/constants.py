class EngineConstants:
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
    
    YELLOW_ORB_MULTIPLIER = 1
    """ The proportion of the player's jump strength that a yellow orb gives. """
    PURPLE_ORB_MULTIPLIER = 0.7
    """ The proportion of the player's jump strength that a purple orb gives. """
    RED_ORB_MULTIPLIER = 2.2
    """ The proportion of the player's jump strength that a red orb gives. """
    
    BLUE_ORB_STARTING_VELOCITY = 3
    """ The yvel that the player gets when they hit a blue orb. (obviously the sign changes based on grav) """

    SOLID_SURFACE_LENIENCY = 0.2
    """ How much we can "fall into/jump into" a solid object before we are considered to have crashed into it instead of gliding on top. kinda buggy when yvel changes a lot. """
    
    PHYSICS_FRAMERATE = 60
    
    QUIT_KEYS = ['q', 'ctrl+c']
    JUMP_KEYS = [' ', 'up', 'w']
    PAUSE_KEYS = ['p', '', 'esc']
    CHECKPOINT_KEYS = ['z']
    REMOVE_CHECKPOINT_KEYS = ['x']
    ALL_KEYS = set(QUIT_KEYS + JUMP_KEYS + PAUSE_KEYS + CHECKPOINT_KEYS + REMOVE_CHECKPOINT_KEYS)

class SPEEDS:
    half = 0.8
    normal = 1
    double = 1.4
    triple = 1.7
    quadruple = 2

    def decode(speedname):
        """
        Get the value of the speed name.
        Currently supported speeds (case sensitive):
        - half (0.8)
        - normal (1)
        - double (1.4)
        - triple (1.7)
        - quadruple (2)

        For example, `SPEEDS.decode("half") -> 0.8`

        Returns `None` if not found. 
        """
        return SPEEDS.__dict__.get(speedname)