from typing import Any, TYPE_CHECKING
from gd_constants import GDConstants
from logger import Logger

if TYPE_CHECKING:
    from level import ObjectData

class OBJECTS:
    """
    Class which stores backend object data for all objects in the game.
    
    An explicit order for elements is kept (mainly for level editor usage).
    
    Object dicts are stored in `OBJECTS.MASTERLIST`.
    """
    
    MASTERLIST = {
        "yellow_orb": {
            "name": "yellow_orb",
            "hitbox_xrange": [-0.3, 1.3],
            "hitbox_yrange": [-0.3, 1.3],
            "hitbox_type": "any-touch", 
            "collide_effect": "yellow-orb",
            "requires_click": True, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },
        "blue_orb": {
            "name": "blue_orb",
            "hitbox_xrange": [-0.3, 1.3],
            "hitbox_yrange": [-0.3, 1.3],
            "hitbox_type": "any-touch", 
            "collide_effect": "blue-orb",
            "requires_click": True, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },
        "purple_orb": {
            "name": "purple_orb",
            "hitbox_xrange": [-0.3, 1.3],
            "hitbox_yrange": [-0.3, 1.3],
            "hitbox_type": "any-touch",
            "collide_effect": "purple-orb",
            "requires_click": True, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },
        "green_orb": {
            "name": "green_orb",
            "hitbox_xrange": [-0.3, 1.3],
            "hitbox_yrange": [-0.3, 1.3],
            "hitbox_type": "any-touch",
            "collide_effect": "green-orb",
            "requires_click": True, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },
        "red_orb": {
            "name": "red_orb",
            "hitbox_xrange": [-0.3, 1.3],
            "hitbox_yrange": [-0.3, 1.3],
            "hitbox_type": "any-touch",
            "collide_effect": "red-orb",
            "requires_click": True, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },
        "black_orb": {
            "name": "black_orb",
            "hitbox_xrange": [-0.3, 1.3],
            "hitbox_yrange": [-0.3, 1.3],
            "hitbox_type": "any-touch", 
            "collide_effect": "black-orb",
            "requires_click": True, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        }  ,  
        "yellow_pad": {
            "name": "yellow_pad",
            "hitbox_xrange": [0, 1],
            "hitbox_yrange": [0, 0.5],
            "hitbox_type": "any-touch",
            "collide_effect": "yellow-pad",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },
        "purple_pad": {
            "name": "purple_pad",
            "hitbox_xrange": [0, 1],
            "hitbox_yrange": [0, 0.5],
            "hitbox_type": "any-touch",
            "collide_effect": "purple-pad",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },
        "blue_pad": {
            "name": "blue_pad",
            "hitbox_xrange": [0, 1],
            "hitbox_yrange": [0, 0.5],
            "hitbox_type": "any-touch",
            "collide_effect": "blue-pad",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },
        "red_pad": {
            "name": "red_pad",
            "hitbox_xrange": [0, 1],
            "hitbox_yrange": [0, 0.5],
            "hitbox_type": "any-touch",
            "collide_effect": "red-pad",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        },        
        "glow_corner": {
            "name": "glow_corner",
            "invis": True,
            "hitbox_type": None, # deco 
            "color_channels": 1,
        },
        "glow_edge": {
            "name": "glow_edge",
            "invis": True,
            "hitbox_type": None, # deco 
            "color_channels": 1,
        },
    }
    """ A Dictionary mapping object types (names) to backend object data. 
    Contains definitions for all objects in the game. """
    
    for blocktype in range(3):
        for i in range(12):
            locals()["MASTERLIST"][f"block{blocktype}_{i}"] = {
                "name": f"block{blocktype}_{i}",
                "hitbox_xrange": [0, 1],
                "hitbox_yrange": [0, 1],
                "hitbox_type": "solid", # activate when crash into side or bottom,
                "collide_effect": "crash-block",
                "requires_click": False, # if player needs to click to activate
                "multi_activate": False,
                "color_channels": 2,
            }
        
    for i in range(10): # TODO - some spikes have smaller hitboxes
        locals()["MASTERLIST"][f"spike{i}"] = {
            "name": f"spike{i}",
            "hitbox_xrange": [0.3, 0.7],
            "hitbox_yrange": [0.2, 0.7],
            "hitbox_type": "any-touch", # activate on any hitbox touch.
            "collide_effect": "crash-obstacle",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 2,
        }
    
    for gravity in GDConstants.gravities:
        locals()["MASTERLIST"][f"grav_portal_{gravity.value}"] ={
            "name": f"grav_portal_{gravity.value}",
            "hitbox_xrange": [0.1, 0.9],
            "hitbox_yrange": [-1.4, 1.4],
            "hitbox_type": "any-touch", # phase through,
            "collide_effect": f"gravity-{gravity.value}",
            "requires_click": False, # if player needs to click to activate
            "color_channels": 0,
        }
    
    for speed in GDConstants.speeds:
        locals()["MASTERLIST"][f"speed_portal_{speed.value}"] = {
            "name": f"speed_portal_{speed.value}",
            "hitbox_xrange": [0, 1],
            "hitbox_yrange": [-0.3, 0.3],
            "hitbox_type": "any-touch", # die on any hitbox touch.
            "collide_effect": f"speed-{speed.value}",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        }
        
    for gamemode in GDConstants.gamemodes:
        locals()["MASTERLIST"][f"mode_portal_{gamemode.value}"] = {
            "name": f"mode_portal_{gamemode.value}",
            "hitbox_xrange": [0.1, 0.9],
            "hitbox_yrange": [-1.4, 1.4],
            "hitbox_type": "any-touch", # die on any hitbox touch.
            "collide_effect": f"gamemode-{gamemode.value}",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        }
        
    OBJECT_NAMES = list(MASTERLIST)
    """ An ordered list of the names (types) of all objects in the game. """
    
    def get_next_object_name(curr_obj_name: str) -> str:
        """ Returns the name of the next object in the master object list. 
        Wraps around if last element. If obj_name does not exist, raise a ValueError. """
        curr_idx = OBJECTS.OBJECT_NAMES.index(curr_obj_name)
        next_idx = (curr_idx + 1) % len(OBJECTS.OBJECT_NAMES)
        
        return OBJECTS.OBJECT_NAMES[next_idx]
    
    def get_prev_object_name(curr_obj_name: str) -> str:
        """ Returns the name of the prev object in the master object list. 
        Wraps around if last element. If obj_name does not exist, raise a ValueError. """
        curr_idx = OBJECTS.OBJECT_NAMES.index(curr_obj_name)
        next_idx = (curr_idx - 1) % len(OBJECTS.OBJECT_NAMES)
        
        return OBJECTS.OBJECT_NAMES[next_idx]
    
    def get(key: str) -> "ObjectData":
        """ Get the ObjectData dict of the object with the given key (name), or None if not found. """
        #Logger.log(f"[OBJECTS/get]: getting key={key} from MASTERLIST, which has size={len(OBJECTS.MASTERLIST)}")
        return OBJECTS.MASTERLIST.get(key, None)
