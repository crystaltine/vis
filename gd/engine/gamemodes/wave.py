from logger import Logger
from time import time_ns
from typing import TYPE_CHECKING
from keyboard.keyboard_listener import KeyboardListener
from engine.constants import EngineConstants

if TYPE_CHECKING:
    from engine.player import Player

def tick_wave(player: "Player", timedelta: float) -> None:
    """ 
    Physics tick for the player in the wave gamemode
    (no jump/gravity - yvel is constant, based solely on if jump key is HELD or not)
    
    This function should be called by a generalized 'tick' function inside
    the player class if the player's current gamemode is ball.
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
    
    # otherwise, apply yvel based on if jump key is held or not
    else:
        player.in_air = True
        
        holding = False
        for jump_key in EngineConstants.JUMP_KEYS:
            if KeyboardListener.is_held(jump_key):
                holding = True
                break
        
        player.yvel = EngineConstants.BLOCKS_PER_SECOND * player.speed * (1 if holding else -1)
    
    Logger.log(f"wave yvel: {player.yvel:.2f}, pos={player.pos[0]:.2f},{player.pos[1]:.2f}")
    player.pos[1] += player.yvel * timedelta
