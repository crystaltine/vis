from gd_constants import GDConstants

class OBJECTS:
    
    for i in range(12):
        locals()[f"block0_{i}"] = {
            "name": f"block0_{i}",
            "hitbox_xrange": [0, 1],
            "hitbox_yrange": [0, 1],
            "hitbox_type": "solid", # die when crash into side or bottom,
            "collide_effect": "crash-block",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
        }
        
    for i in range(10): # TODO - some spikes have smaller hitboxes
        locals()[f"spike{i}"] = {
            "name": f"spike{i}",
            "hitbox_xrange": [0.3, 0.7],
            "hitbox_yrange": [0.2, 0.7],
            "hitbox_type": "any-touch", # die on any hitbox touch.
            "collide_effect": "crash-spike",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
        }
        
    yellow_orb = {
        "name": "yellow_orb",
        "hitbox_xrange": [-0.3, 1.3],
        "hitbox_yrange": [-0.3, 1.3],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "yellow-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
    }
    blue_orb = {
        "name": "blue_orb",
        "hitbox_xrange": [-0.3, 1.3],
        "hitbox_yrange": [-0.3, 1.3],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "blue-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
    }
    purple_orb = {
        "name": "purple_orb",
        "hitbox_xrange": [-0.3, 1.3],
        "hitbox_yrange": [-0.3, 1.3],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "purple-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
    }
    green_orb = {
        "name": "green_orb",
        "hitbox_xrange": [-0.3, 1.3],
        "hitbox_yrange": [-0.3, 1.3],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "green-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
    }
    red_orb = {
        "name": "red_orb",
        "hitbox_xrange": [-0.3, 1.3],
        "hitbox_yrange": [-0.3, 1.3],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "red-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
    }
    black_orb = {
        "name": "black_orb",
        "hitbox_xrange": [-0.3, 1.3],
        "hitbox_yrange": [-0.3, 1.3],
        "hitbox_type": "any-touch", # die on any hitbox touch.
        "collide_effect": "black-orb",
        "requires_click": True, # if player needs to click to activate
        "multi_activate": False,
    }    
    
    for gravity in GDConstants.gravities:
        locals()[f"grav_portal_{gravity.value}"] ={
            "name": f"grav_portal_{gravity.value}",
            "hitbox_xrange": [0.1, 0.9],
            "hitbox_yrange": [-1.4, 1.4],
            "hitbox_type": "any-touch", # phase through,
            "collide_effect": f"gravity-{gravity.value}",
            "requires_click": False, # if player needs to click to activate
        }
    
    for speed in GDConstants.speeds:
        locals()[f"speed_{speed.value}"] = {
            "name": f"speed_{speed.value}",
            "hitbox_xrange": [0, 1],
            "hitbox_yrange": [-0.3, 0.3],
            "hitbox_type": "any-touch", # die on any hitbox touch.
            "collide_effect": f"speed-{speed.value}",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
        }
        
    for gamemode in GDConstants.gamemodes:
        locals()[f"mode_portal_{gamemode.value}"] = {
            "name": f"mode_portal_{gamemode.value}",
            "hitbox_xrange": [0.1, 0.9],
            "hitbox_yrange": [-1.4, 1.4],
            "hitbox_type": "any-touch", # die on any hitbox touch.
            "collide_effect": f"gamemode-{gamemode.value}",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
        }