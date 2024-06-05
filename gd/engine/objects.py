from typing import Any, TYPE_CHECKING
from gd_constants import GDConstants
from logger import Logger

if TYPE_CHECKING:
    from level import ObjectData

class OBJECTS:
    
    masterlist = {
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
        
    for blocktype in range(3):
        for i in range(12):
            locals()["masterlist"][f"block{blocktype}_{i}"] = {
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
        locals()["masterlist"][f"spike{i}"] = {
            "name": f"spike{i}",
            "hitbox_xrange": [0.3, 0.7],
            "hitbox_yrange": [0.2, 0.7],
            "hitbox_type": "any-touch", # activate on any hitbox touch.
            "collide_effect": "crash-spike",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 2,
        }
    
    for gravity in GDConstants.gravities:
        locals()["masterlist"][f"grav_portal_{gravity.value}"] ={
            "name": f"grav_portal_{gravity.value}",
            "hitbox_xrange": [0.1, 0.9],
            "hitbox_yrange": [-1.4, 1.4],
            "hitbox_type": "any-touch", # phase through,
            "collide_effect": f"gravity-{gravity.value}",
            "requires_click": False, # if player needs to click to activate
            "color_channels": 0,
        }
    
    for speed in GDConstants.speeds:
        locals()["masterlist"][f"speed_portal_{speed.value}"] = {
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
        locals()["masterlist"][f"mode_portal_{gamemode.value}"] = {
            "name": f"mode_portal_{gamemode.value}",
            "hitbox_xrange": [0.1, 0.9],
            "hitbox_yrange": [-1.4, 1.4],
            "hitbox_type": "any-touch", # die on any hitbox touch.
            "collide_effect": f"gamemode-{gamemode.value}",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
        }
        
    all_obj_names = list(masterlist.keys())
    
    def get_next_object_name(obj_name: str) -> str:
        """ Returns the name of the next object in the master object list. 
        Wraps around if last element. If obj_name does not exist, raise a ValueError. """
        curr_idx = OBJECTS.all_obj_names.index(obj_name)
        next_idx = (curr_idx + 1) % len(OBJECTS.all_obj_names)
        
        return OBJECTS.all_obj_names[next_idx]
    
    def get_prev_object_name(obj_name: str) -> str:
        """ Returns the name of the prev object in the master object list. 
        Wraps around if last element. If obj_name does not exist, raise a ValueError. """
        curr_idx = OBJECTS.all_obj_names.index(obj_name)
        next_idx = (curr_idx - 1) % len(OBJECTS.all_obj_names)
        
        return OBJECTS.all_obj_names[next_idx]
    
    def get(key: str) -> "ObjectData":
        """ Get the ObjectData dict of the object with the given key (name), or None if not found. """
        #Logger.log(f"[OBJECTS/get]: getting key={key} from masterlist, which has size={len(OBJECTS.masterlist)}")
        return OBJECTS.masterlist.get(key, None)
