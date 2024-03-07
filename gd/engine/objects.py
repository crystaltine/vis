class OBJECTS:
    block = {
        "name": "block",
        "hitbox_xrange": [0, 1],
        "hitbox_yrange": [0, 1],
        "hitbox_type": "solid", # die when crash into side or bottom,
        "collide_effect": "crash-block",
        "requires_click": False, # if player needs to click to activate
        "multi_activate": False,
        "has_been_activated": False
    }
    spike = {
        "name": "spike",
        "hitbox_xrange": [0.3, 0.7],
        "hitbox_yrange": [0.2, 0.7],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "crash-spike",
        "requires_click": False, # if player needs to click to activate
        "multi_activate": False,
        "has_been_activated": False
    }
    yellow_orb = {
        "name": "yellow_orb",
        "hitbox_xrange": [-0.2, 1.2],
        "hitbox_yrange": [0.2, 1.2],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "yellow-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
        "has_been_activated": False
    }
    blue_orb = {
        "name": "blue_orb",
        "hitbox_xrange": [-0.2, 1.2],
        "hitbox_yrange": [0.2, 1.2],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "blue-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
        "has_been_activated": False
    }
    purple_orb = {
        "name": "purple_orb",
        "hitbox_xrange": [-0.2, 1.2],
        "hitbox_yrange": [0.2, 1.2],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "purple-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
        "has_been_activated": False
    }
    yellow_grav_portal = {
        "name": "yellow_grav_portal",
        "hitbox_xrange": [0.1, 0.9],
        "hitbox_yrange": [-1.4, 1.4],
        "hitbox_type": "any-touch", # phase through,
        "collide_effect": "neg-gravity",
        "requires_click": False, # if player needs to click to activate,
        "has_been_activated": False
    }
    blue_grav_portal = {
        "name": "blue_grav_portal",
        "hitbox_xrange": [0.1, 0.9],
        "hitbox_yrange": [-1.4, 1.4],
        "hitbox_type": "any-touch", # phase through,
        "collide_effect": "pos-gravity",
        "requires_click": False, # if player needs to click to activate
        "has_been_activated": False
    }