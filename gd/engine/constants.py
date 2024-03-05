class CONSTANTS:
    BLOCKS_PER_SECOND = 5
    GRAVITY = 5
    TERMINAL_VEL = 10

    PLAYER_HITBOX_X = 1
    PLAYER_HITBOX_Y = 1

    SOLID_SURFACE_LENIENCY = 0.2

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

class OBJECTS:
    block = {
        "name": "block",
        "hitbox_xrange": [0, 1],
        "hitbox_yrange": [0, 1],
        "hitbox_type": "solid" # die when crash into side
    }
    spike = {
        "name": "spike",
        "hitbox_xrange": [0.3, 0.7],
        "hitbox_yrange": [0.2, 0.7],
        "hitbox_type": "hostile" # die on any hitbox touch
    }
    yellow_grav_portal = {
        "name": "yellow_grav_portal",
        "hitbox_xrange": [0.1, 0.9],
        "hitbox_yrange": [-1.4, 1.4],
        "hitbox_type": "ghost", # phase through,
        "effect": "neg-gravity"
    }
    blue_grav_portal = {
        "name": "blue_grav_portal",
        "hitbox_xrange": [0.1, 0.9],
        "hitbox_yrange": [-1.4, 1.4],
        "hitbox_type": "ghost", # phase through,
        "effect": "pos-gravity"
    }