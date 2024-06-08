class EngineConstants:
    BLOCKS_PER_SECOND = 8.5
    GRAVITY = 55
    PLAYER_JUMP_STRENGTH = 16
    """ How much the player's yvel is set to when they jump. """
    TERMINAL_VEL = 30
    """ The maximum downward velocity the player can accumulate due to GRAVITY (can exceed if using a black orb, for example). """

    CUBE_GRAVITY_MULTIPLIER = 1
    BALL_GRAVITY_MULTIPLIER = 0.8
    UFO_GRAVITY_MULTIPLIER = 0.7

    PLAYER_HITBOX_X = 1
    PLAYER_HITBOX_Y = 1
    PLAYER_WAVE_HITBOX_X = 0.4
    PLAYER_WAVE_HITBOX_Y = 0.4
    
    COOLDOWN_BETWEEN_ATTEMPTS = 1
    
    YELLOW_ORB_MULTIPLIER = 1
    """ The proportion of the player's jump strength that a yellow orb gives. """
    YELLOW_PAD_MULTIPLIER = 2
    """ The proportion of the player's jump strength that a yellow pad gives """
    PURPLE_ORB_MULTIPLIER = 0.7
    """ The proportion of the player's jump strength that a purple orb gives. """
    PURPLE_PAD_MULTIPLIER = 0.95
    """ The proportion of the player's jump strength that a purple pad gives. """
    RED_ORB_MULTIPLIER = 2
    """ The proportion of the player's jump strength that a red orb gives. """
    RED_PAD_MULTIPLIER = 2.5
    """ The proportion of the player's jump strength that a red pad gives."""
    BLACK_ORB_VELOCITY = 20
    """ What the player's y-vel gets set to when hitting a black orb (sign changes based on gravity) """
    
    BLUE_ORB_STARTING_VELOCITY = 3
    """ The yvel that the player gets when they hit a blue orb. (obviously the sign changes based on grav) """

    BALL_STARTING_VELOCITY = 4
    """ The yvel the player gets when they switch gravity in ball mode. """

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