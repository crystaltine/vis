from logger import Logger
from time import time_ns
from typing import TYPE_CHECKING
from keyboard.keyboard_listener import KeyboardListener
from engine.constants import EngineConstants
from engine.catch_player import catch_player
from gd_constants import GDConstants

if TYPE_CHECKING:
    from engine.player import Player

def tick_ship(player: "Player", timedelta: float) -> None:
    """ 
    Physics tick for the player in the ship gamemode
    (no jump - constant accel while holding UNTIL yvel passes max)
    
    This function should be called by a generalized 'tick' function inside
    the player class if the player's current gamemode is ship.
    """
    
    #Logger.log(f"Tick: td={timedelta}, pos={player.pos[0]:.2f},{player.pos[1]:.2f}, yvel={player.yvel:.2f}, jump_req={player.jump_requested}, in_air={player.in_air}, grav_dir={player.gravity}")
    #Logger.log(f"^^^: collisions: {[(collision.obj.data['name'], collision.vert_coord, collision.vert_side) for collision in player.curr_collisions]}")
    
    # always move right no matter what
    player.pos[0] += player.speed * EngineConstants.BLOCKS_PER_SECOND * timedelta
    
    # hitting ground allows for yvel=0 glide
    if player.pos[1] < 0 and player.yvel < 0: # if we are going up, we shouldnt hit the ground
        #Logger.log(f"Hit ground. setting y-pos to 0 and in_air to False")
        player.pos[1] = 0
        player.yvel = 0
        player.in_air = False  
        #Logger.log(f"[wve] on ground!!!!!")
    
    # otherwise, apply yvel based on if jump key is held or not
    else:
        player.in_air = True
        
        holding = False
        for jump_key in GDConstants.JUMP_KEYS:
            if KeyboardListener.is_held(jump_key):
                holding = True
                break
        
        #if -EngineConstants.SHIP_TERMINAL_VEL < player.yvel < EngineConstants.SHIP_TERMINAL_VEL:
        if holding: # if we are holding jump, apply acceleration
            if player.yvel < EngineConstants.SHIP_TERMINAL_VEL:
                player.yvel += player.gravity * EngineConstants.SHIP_GRAVITY_MULTIPLIER_UP * timedelta
        else: # if we are not holding jump, apply gravity
            if player.yvel > -EngineConstants.SHIP_TERMINAL_VEL:
                player.yvel -= player.gravity * EngineConstants.SHIP_GRAVITY_MULTIPLIER_DOWN * timedelta  
    
        catch_player(player, timedelta, gravity_override='falling' if player.yvel < 0 else 'rising')
        # we have to override here because catch player determines direction based on accel
    
        player.pos[1] += player.yvel * timedelta
        Logger.log(f"[SHIPPPPPPPPP AFTER CATCH] player ypos={player.pos[1]}, yvel={player.yvel} grav={player.gravity}")
        #Logger.log(f"[2] wave yvel: {player.yvel:.2f}, pos={player.pos[0]:.2f},{player.pos[1]:.2f}")
        if player.pos[1] < 0: # catch spasming on ground (for animation function)
            player.yvel = 0
            player.pos[1] = 0