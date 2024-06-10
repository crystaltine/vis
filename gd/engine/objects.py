from typing import Any, TYPE_CHECKING
from gd_constants import GDConstants
from logger import Logger

if TYPE_CHECKING:
    from level import ObjectData

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
        "glow_corner": {
            "name": "glow_corner",
            "hitbox_type": None, # deco 
            "color_channels": 1,
            "texture_path": "./assets/objects/deco/glow_corner.png"
        },
        "glow_edge": {
            "name": "glow_edge",
            "hitbox_type": None, # deco 
            "color_channels": 1,
            "texture_path": "./assets/objects/deco/glow_edge.png"
        },
        "chain_base": {
            "name": "chain_bottom",
            "hitbox_type": None, # deco
            "color_channels": 1,
            "texture_path": "./assets/objects/deco/chain_base.png"
        },
        "chain_middle": {
            "name": "chain_middle",
            "hitbox_type": None, # deco
            "color_channels": 1,
            "texture_path": "./assets/objects/deco/chain_middle.png"
        },
        "fake_spike_0": {
            "name": "fake_spike_0",
            "hitbox_type": None, # deco
            "color_channels": 1,
            "texture_path": "./assets/objects/deco/fake_spike_0.png"
        },
        "fake_spike_1": {
            "name": "fake_spike_1",
            "hitbox_type": None, # deco
            "color_channels": 1,
            "texture_path": "./assets/objects/deco/fake_spike_1.png"
        },
        "color_trigger": {
            "name": "color_trigger",
            "invisible": True, # invisible to player, visible on editor
            "hitbox_type": None, # deco
            "color_channels": 1,
            "texture_path": "./assets/objects/triggers/color_trigger.png"
        }
    }
    """ A Dictionary mapping object types (names) to backend object data. 
    Contains definitions for all objects in the game. """         
    
    for blocktype in range(3):
        for i in range(GDConstants.NUM_BLOCK_TEXTURES):
            locals()["MASTERLIST"][f"block{blocktype}_{i}"] = {
                "name": f"block{blocktype}_{i}",
                "hitbox_xrange": [0, 1],
                "hitbox_yrange": [0, 1],
                "hitbox_type": "solid", # activate when crash into side or bottom,
                "collide_effect": "crash-block",
                "requires_click": False, # if player needs to click to activate
                "multi_activate": False,
                "color_channels": 2,
                "texture_path": f"./assets/objects/block/block{blocktype}/{i}.png"
            }
        
    for i in range(GDConstants.NUM_SPIKE_TALL_TEXTURES):
        locals()["MASTERLIST"][f"spike_tall{i}"] = {
            "name": f"spike_tall{i}",
            "hitbox_xrange": [0.25, 0.75],
            "hitbox_yrange": [0.1, 0.7],
            "hitbox_type": "any-touch", # activate on any hitbox touch.
            "collide_effect": "crash-obstacle",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 2,
            "texture_path": f"./assets/objects/obstacle/spike_tall/spike_tall{i}.png"
        }
    for i in range(GDConstants.NUM_SPIKE_SHORT_TEXTURES):
        locals()["MASTERLIST"][f"spike_short{i}"] = {
            "name": f"spike_short{i}",
            "hitbox_xrange": [0.25, 0.75],
            "hitbox_yrange": [0.1, 0.35],
            "hitbox_type": "any-touch", # activate on any hitbox touch.
            "collide_effect": "crash-obstacle",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 2,
            "texture_path": f"./assets/objects/obstacle/spike_short/spike_short{i}.png"
        }
    for i in range(GDConstants.NUM_SPIKE_FLAT_TEXTURES):
        locals()["MASTERLIST"][f"spike_flat{i}"] = {
            "name": f"spike_flat{i}",
            "hitbox_xrange": [0.25, 0.75],
            "hitbox_yrange": [0.1, 0.25],
            "hitbox_type": "any-touch", # activate on any hitbox touch.
            "collide_effect": "crash-obstacle",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 2,
            "texture_path": f"./assets/objects/obstacle/spike_flat/spike_flat{i}.png"
        }
        
    for orbtype in GDConstants.orb_types:
        locals()["MASTERLIST"][f"{orbtype.value}_orb"] = {
            "name": f"{orbtype.value}_orb",
            "hitbox_xrange": [-0.3, 1.3],
            "hitbox_yrange": [-0.3, 1.3],
            "hitbox_type": "any-touch", 
            "collide_effect": f"{orbtype.value}-orb",
            "requires_click": True, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
            "texture_path": f"./assets/objects/effect/orbs/orb_{orbtype.value}.png",
        }  
        
    for padtype in GDConstants.pad_types:
        locals()["MASTERLIST"][f"{padtype.value}_pad"] = {
            "name": f"{padtype.value}_pad",
            "hitbox_xrange": [0, 1],
            "hitbox_yrange": [0, 0.5],
            "hitbox_type": "any-touch",
            "collide_effect": f"{padtype.value}-pad",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
            "texture_path": f"./assets/objects/effect/pads/pad_{padtype.value}.png"
        }   
    
    for gravity in GDConstants.gravities:
        locals()["MASTERLIST"][f"grav_portal_{gravity.value}"] ={
            "name": f"grav_portal_{gravity.value}",
            "hitbox_xrange": [0.1, 0.9],
            "hitbox_yrange": [-1.4, 1.4],
            "hitbox_type": "any-touch", # phase through,
            "collide_effect": f"gravity-{gravity.value}",
            "requires_click": False, # if player needs to click to activate
            "multi_activate": False,
            "color_channels": 0,
            "texture_path": f"./assets/objects/effect/grav_portals/grav_portal_{gravity.value}.png"
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
            "texture_path": f"./assets/objects/effect/speed_portals/speed_portal_{speed.value}.png"
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
            "texture_path": f"./assets/objects/effect/mode_portals/mode_portal_{gamemode.value}.png"
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
    
    def get_num_color_channels(key: str) -> int:
        """ Get the number of color channels of the object with the given key (name). """
        return OBJECTS.get(key)["color_channels"]
