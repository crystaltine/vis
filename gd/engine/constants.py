class EngineConstants:
    BLOCKS_PER_SECOND = 8.5
    GRAVITY = 65
    PLAYER_JUMP_STRENGTH = 18
    """ How much the player's yvel is set to when they jump. """
    UFO_JUMP_STRENGTH = 14
    """ How much the player's yvel is set to when they jump in UFO mode. """
    TERMINAL_VEL = 30
    """ The maximum downward velocity the player can accumulate due to GRAVITY (can exceed if using a black orb, for example). """
    SHIP_TERMINAL_VEL = 9.5
    
    MAX_LEVEL_Y = 100
    """ The maximum y value that the player can reach, otherwise crash """

    CUBE_GRAVITY_MULTIPLIER = 1
    SHIP_GRAVITY_MULTIPLIER_UP = 1
    SHIP_GRAVITY_MULTIPLIER_DOWN = 0.75
    BALL_GRAVITY_MULTIPLIER = 0.85
    UFO_GRAVITY_MULTIPLIER = 0.67    
    
    END_OF_LEVEL_PADDING = 10
    """ The distance in blocks from the last object in a level to when the player is considered to have finished the level. """

    PLAYER_HITBOX_X = 1
    PLAYER_HITBOX_Y = 1
    PLAYER_WAVE_HITBOX_X = 0.5
    PLAYER_WAVE_HITBOX_Y = 0.5
    
    SHIP_TEXTURE_CHANGE_THRESHOLD_1 = 2
    """ What the player's yvel needs to exceed in ship mode in order to change to the semi-down/up pointing texture. """
    SHIP_TEXTURE_CHANGE_THRESHOLD_2 = 5
    """ What the player's yvel needs to exceed in ship mode in order to change to the diagonally-down/up pointing texture. """
    
    COOLDOWN_BETWEEN_ATTEMPTS = 1
    
    YELLOW_ORB_MULTIPLIER = 1
    """ The proportion of the player's jump strength that a yellow orb gives. """
    YELLOW_PAD_MULTIPLIER = 1.3
    """ The proportion of the player's jump strength that a yellow pad gives """
    PURPLE_ORB_MULTIPLIER = 0.73
    """ The proportion of the player's jump strength that a purple orb gives. """
    PURPLE_PAD_MULTIPLIER = 0.95
    """ The proportion of the player's jump strength that a purple pad gives. """
    RED_ORB_MULTIPLIER = 1.55
    """ The proportion of the player's jump strength that a red orb gives. """
    RED_PAD_MULTIPLIER = 1.7
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