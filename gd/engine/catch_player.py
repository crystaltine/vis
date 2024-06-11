from typing import TYPE_CHECKING, Literal
from math import floor, ceil
from engine.constants import EngineConstants
from logger import Logger

if TYPE_CHECKING:
    from engine.player import Player
    
def catch_player(player: "Player", timedelta: float, gravity_override: Literal['falling', 'rising'] = None) -> bool:
    """ "Catches" the player from falling through the ground due to super high yvelocity.
    
    Basically, this function checks if the player's current y-vel would lead them to be inside
    a SOLID object by the time ypos updates to the next value. If it will, then this function
    sets the ypos to be gliding along that solid object and sets yvel to 0.
    
    Returns whether or not player yvel/ypos was updated.
    """
    
    new_y_pos = player.pos[1] + player.yvel * timedelta
    
    #Logger.log(f"[catch_player], curr y is {player.pos[1]}, new y is {new_y_pos}")
    #Logger.log(f"[CATCH], player y={player.pos[1]:4f}, orig yvel={player.yvel:4f} projected new pos: {new_y_pos:4f}")
    if crossing_intval(player.pos[1], new_y_pos):
        if gravity_override == 'falling' or (player.gravity > 0 and gravity_override is None):
            closest_surface = player.game.collision_handler.highest_solid_object_beneath_player(timedelta)
            #Logger.log(f"[catch_player], grav>0: closest surface is {closest_surface}")
            if closest_surface is not None:
                if new_y_pos <= closest_surface.y + closest_surface.data.get("hitbox_yrange")[1]:
                    # there is a ground below to catch us
                    Logger.log(f"[CATCH BELOW ACTIVATED], closest y={closest_surface.y}")
                    player.yvel = 0
                    player.in_air = False
                    player.pos[1] = closest_surface.y + closest_surface.data.get("hitbox_yrange")[1]
                    return True
                #else:
                # no relevant surface, just update ypos normally
                    
        elif gravity_override == 'rising' or player.gravity < 0: # falling up
            closest_surface = player.game.collision_handler.lowest_solid_object_above_player(timedelta)
            if closest_surface is not None:
                if new_y_pos + EngineConstants.PLAYER_HITBOX_Y >= closest_surface.y + closest_surface.data.get("hitbox_yrange")[0]:
                    # there is a ground below to catch us
                    
                    Logger.log(f"[CATCH ABOVE ACTIVATED], closest y={closest_surface.y}")
                    player.yvel = 0
                    player.in_air = False
                    player.pos[1] = closest_surface.y + closest_surface.data.get("hitbox_yrange")[0] - EngineConstants.PLAYER_HITBOX_Y
                    return True
    
    # if we wont cross an integer, just dont care
    return False

def crossing_intval(num1: float, num2: float) -> bool:
    """ Returns if num1 and num2 are part of different integer intervals. 
    
    HOWEVER: if exactly one of the nums is an int, returns True. 
    """
    if num1.is_integer() and not num2.is_integer():
        return True
    if not num1.is_integer() and num2.is_integer():
        return True
    
    return floor(num1) != floor(num2)