from math import floor
from time import time_ns
from typing import TYPE_CHECKING

from logger import Logger
from engine.constants import EngineConstants
from engine.collision_handler import CollisionHandler

if TYPE_CHECKING:
    from engine.player import Player

def tick_cube(player: "Player", timedelta: float) -> None:
    """ 
    Physics tick for the player in the cube gamemode
    
    Now in its own separate function so gamemodes can be organized.
    This function should be called by a generalized 'tick' function inside
    the player class if the player's current gamemode is cube.
    """
    
    #Logger.log(f"Tick: td={timedelta}, pos={player.pos[0]:.2f},{player.pos[1]:.2f}, yvel={player.yvel:.2f}, jump_req={player.jump_requested}, in_air={player.in_air}, grav_dir={player.gravity}")
    #Logger.log(f"^^^: collisions: {[(collision.obj.data['name'], collision.vert_coord, collision.vert_side) for collision in player.curr_collisions]}")
    
    # always move right no matter what
    player.pos[0] += player.speed * EngineConstants.BLOCKS_PER_SECOND * timedelta
    
    # GLIDE HANDLING BELOW (setting y-values)
    
    # if y < 0, then we just hit ground and should just set y=0, yvel=0, in_air=False
    if player.pos[1] <= 0 and player.yvel <= 0: # if we are going up, we shouldnt hit the ground
        #Logger.log(f"Hit ground. setting y-pos to 0 and in_air to False")
        player.pos[1] = 0
        player.yvel = 0
        player.in_air = False            
    
    # if gravity is + (down) and we have a "top" collision, adjust the y position to be on top of the block
    elif (player.gravity > 0 and any(collision.vert_side == "top" for collision in player.curr_collisions)):
        if player.yvel < 0: # only care if we are going down
            player.pos[1] = max([collision.vert_coord for collision in player.curr_collisions if collision.vert_side == "top"])
            player.yvel = 0
            
            #Logger.log(f"reg gravity: setting y-pos to {player.pos[1]:.2f} and in_air to False")
            player.in_air = False
    
    # if gravity is - (up) and we have a "bottom" collision, adjust the y position to be on top of the block
    elif (player.gravity < 0 and any(collision.vert_side == "bottom" for collision in player.curr_collisions)):
        if player.yvel > 0: # only hit ground if we are going up
            # we have to subtract the player hitbox yrange to get the top of the player
            player.pos[1] = min([collision.vert_coord for collision in player.curr_collisions if collision.vert_side == "bottom"])-EngineConstants.PLAYER_HITBOX_Y
            player.yvel = 0
            
            #Logger.log(f"rev gravity: setting y-pos to {player.pos[1]:.2f} and in_air to False")
            player.in_air = False
    
    # otherwise are in mid-air and should apply gravity
    else:
        #Logger.log(f"seems like we are in the air, in_air -> true after this.")
        player.in_air = True
        
        if not player.yvel <= -EngineConstants.TERMINAL_VEL: # if we are not at terminal velocity, apply gravity
            player.yvel -= player.gravity * EngineConstants.CUBE_GRAVITY_MULTIPLIER * timedelta
        
        # note that we can still fall faster than terminal velocity 
        # from sources other than gravity, such as black orbs.
    
    # if jump was requested and we are not in the air, set the jump physics
    if player.jump_requested and not player.in_air:
        player._jump()
        player.jump_requested = False
        
    if not player.in_air:
        player.last_on_ground_time = time_ns()
    
    # if player is about to cross an integer y-value, check for ground/ceiling
    new_y_pos = player.pos[1] + player.yvel * timedelta
    if floor(player.pos[1]) != floor(new_y_pos): # crossing int. y val
        if player.yvel < 0: # falling down, look for surface below
            closest_surface = player.collision_handler.highest_solid_object_beneath_player()
            if closest_surface is not None:
                if new_y_pos < closest_surface.y + closest_surface.data.get("hitbox_yrange")[1]:
                    # there is a ground below to catch us
                    player.yvel = 0
                    player.pos[1] = closest_surface.y + closest_surface.data.get("hitbox_yrange")[1]
                #else:
                    # ground is out of range, just update ypos normally
        elif player.yvel > 0: # reverse grav, look for surface above
            closest_surface = player.collision_handler.lowest_solid_object_above_player()
            if closest_surface is not None:
                if new_y_pos < closest_surface.y + closest_surface.data.get("hitbox_yrange")[0]:
                    # there is a ground below to catch us
                    player.yvel = 0
                    player.pos[1] = closest_surface.y + closest_surface.data.get("hitbox_yrange")[0]

            # TODO - verify above code
            
    player.pos[1] += player.yvel * timedelta
    
    # addgroundcheck func here ased on grav
    
    
def jump_cube(player: "Player") -> None:
    player.yvel = EngineConstants.PLAYER_JUMP_STRENGTH * player.sign_of_gravity()
    player.in_air = True