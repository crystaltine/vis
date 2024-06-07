from typing import TYPE_CHECKING
from math import floor
from engine.constants import EngineConstants
from logger import Logger

if TYPE_CHECKING:
    from engine.player import Player
    
def catch_player(player: "Player", timedelta: float) -> bool:
    """ "Catches" the player from falling through the ground due to super high yvelocity.
    Returns True if player y-vel has already been updated (dont update again), False otherwise.
    
    This function can be used in any gravity-effected gamemode that involves gliding along surfaces.
    """
    
    new_y_pos = player.pos[1] + player.yvel * timedelta
    
    Logger.log(f"[catch_player], curr y is {player.pos[1]}, new y is {new_y_pos}")
    
    if floor(player.pos[1]) != floor(new_y_pos): # crossing int. y val
        if player.gravity > 0: # falling down, look for surface below
            closest_surface = player.game.collision_handler.highest_solid_object_beneath_player(timedelta)
            Logger.log(f"[catch_player], grav>0: closest surface is {closest_surface}")
            if closest_surface is not None:
                if new_y_pos <= closest_surface.y + closest_surface.data.get("hitbox_yrange")[1]:
                    # there is a ground below to catch us
                    Logger.log(f"[grav>0] catching player from falling through ground, cloest surface y={closest_surface.y}, player y={player.pos[1]}")
                    player.yvel = 0
                    player.in_air = False
                    player.pos[1] = closest_surface.y + closest_surface.data.get("hitbox_yrange")[1]
                    return True
                #else:
                # no relevant surface, just update ypos normally
                    
        elif player.gravity < 0: # reverse grav, look for surface above
            closest_surface = player.game.collision_handler.lowest_solid_object_above_player(timedelta)
            if closest_surface is not None:
                if new_y_pos + EngineConstants.PLAYER_HITBOX_Y >= closest_surface.y + closest_surface.data.get("hitbox_yrange")[0]:
                    # there is a ground below to catch us
                    
                    Logger.log(f"[grav<0] catching player from falling through ground, cloest surface y={closest_surface.y}, player y={player.pos[1]}")
                    player.yvel = 0
                    player.in_air = False
                    player.pos[1] = closest_surface.y + closest_surface.data.get("hitbox_yrange")[0] - EngineConstants.PLAYER_HITBOX_Y
                    return True
    
    return False