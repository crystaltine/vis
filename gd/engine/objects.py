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