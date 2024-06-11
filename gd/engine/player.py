from typing import List, Tuple, TYPE_CHECKING
from time import time_ns, time
from copy import deepcopy

from logger import Logger
from gd_constants import GDConstants
from engine.constants import EngineConstants, SPEEDS
from engine.collision import Collision
from engine.gamemodes.cube import tick_cube, jump_cube
from engine.gamemodes.ship import tick_ship
from engine.gamemodes.ball import tick_ball, jump_ball
from engine.gamemodes.ufo import tick_ufo, jump_ufo
from engine.gamemodes.wave import tick_wave
from level import StartSettings
from copy import copy

if TYPE_CHECKING:
    from game import Game

class Player:
    """
    Represents the player inside a level and handles physics calculations.
    """
    
    tick_funcs = {
        "cube": tick_cube,
        "ship": tick_ship,
        "ball": tick_ball,
        "ufo": tick_ufo,
        "wave": tick_wave
    }

    def __init__(self, game: "Game", start_settings: StartSettings = {}):
        """
        (OPTIONAL) `start_settings` format (mainly used for startpos):
        ```python
        {
            pos: [int, int], # [x, y] to start at
            speed: "half", "normal", ... "quadruple" # see constants.SPEEDS
            gravity: int # set a starting gravity. EngineConstants.gravity for default, negative that for reverse
        }
        ```

        If a setting isn't provided, default values are used,
        which will spawn a cube at [0,0] with regular speed and gravity.
        """
        self.START_SETTINGS = start_settings
        
        self.speed: GDConstants.speeds = SPEEDS.decode(start_settings["speed"])
        
        self.wave_pivot_points: List[Tuple[int, int]] = []
        """ A persistent list (reset upon crash) that keeps track of whenever the wave changes direction, in order to render the trail. """
        
        self.gamemode: GDConstants.gamemodes = start_settings["gamemode"]
        """ One of "cube", "ship", "ball", "ufo", "wave", "robot", "spider" (swing maybe? idk)"""
        
        self.ORIGINAL_START_POS = copy(start_settings["position"])
        self.pos = copy(start_settings["position"])
        """ [x, y], where x is horiz (progress). BOTTOM LEFT of player. y=0 means on the ground, and y cannot be negative."""

        self.yvel = 0
        Logger.log(f"start settings grav is {start_settings['gravity']}")
        self.gravity = EngineConstants.GRAVITY * (1 if start_settings["gravity"] == "normal" else -1)
        Logger.log(f"self.gravity is {self.gravity}")
        
        self.jump_requested = False
        """ variable to store when the player jumps before the next physics tick. """

        self.last_on_ground_time = 0
        """ Stores the latest time when self.in_air was set to False. Used for calculating cube rotation as we are falling. """
        self.in_air = False
        """ If the player is currently jumping. can't double jump. Jump status is reset to false when the player hits a glidable hitbox. """

        self.game = game
        self.curr_collisions: List[Collision] = []
        """ Maintains a list of objects the player is currently touching. Gets updated on every collision check (physics tick)"""

    def tick(self, timedelta: float):
        """ 
        General physics tick for the player. Calls the appropriate tick function based on the current gamemode.
        """
        
        tickfunc = Player.tick_funcs.get(self.gamemode)
        
        if tickfunc is None:
            raise Exception(f"[Player/tick] gamemode {self.gamemode} not set up in Player.tick()")

        tickfunc(self, timedelta)
        
    def get_dist_from_start(self) -> float:
        """ Get the TRUE distance from the player's starting position, since we start at a negative x. """
        return self.pos[0] - self.ORIGINAL_START_POS[0]
    
    def reset_physics(self, new_pos: Tuple[int, int] = None) -> None:
        """
        Reset to starting physics (yvel=0, in_air=False, etc.)
        This should be used when the player dies or resets.
        Optionally, can select a new position to reset to.
        """
        
        self.pos = new_pos or deepcopy(self.ORIGINAL_START_POS)
        self.in_air = False
        self.yvel = 0
        self.jump_requested = False
        self.wave_pivot_points = []    
        self.curr_collisions.clear()
        self.gamemode = self.START_SETTINGS["gamemode"]
        self.speed = SPEEDS.decode(self.START_SETTINGS["speed"])
        self.gravity = EngineConstants.GRAVITY * (1 if self.START_SETTINGS["gravity"] == "normal" else -1)
        self.last_on_ground_time = time_ns()
    
    def request_jump(self):
        """
        Requests a jump for the next physics tick.
        """
        # NOTE: this is getting moved to each gamemmode's specific jump handler,
        # since you can multi-input in some (such as ufo)
        #if self.in_air: 
        #    #Logger.log(f"XXXXXXXX player tried to jump but cant. pos={self.pos[0]:.2f},{self.pos[1]:.2f}, yvel={self.yvel:.2f}")
        #    return
        
        #Logger.log(f"XXXXXXXX player jumped. pos={self.pos[0]:.2f},{self.pos[1]:.2f}, yvel={self.yvel:.2f}, walking_on={self._walking_on:.2f}, names of colliding objs: {[collision.obj.data['name'] for collision in self.curr_collisions]}")        
        #Logger.log(f"XXXXXXXX player jumped. pos={self.pos[0]:.2f},{self.pos[1]:.2f}, yvel={self.yvel:.2f}, walking_on={self._walking_on:.2f}, names of colliding objs: {[collision.obj.data['name'] for collision in self.curr_collisions]}")        
        self.jump_requested = True
    
    def _jump(self):
        """
        Sets the physics for jumping, depending on the gamemode. Should only be used in `Player.tick()`
        and nowhere else. For external use, use `Player.jump()`.
        """
        
        match self.gamemode:
            case "cube":
                jump_cube(self)
            case "ball":
                jump_ball(self)
            case "ufo":
                jump_ufo(self)
            case _:
                pass # no jump for other gamemodes - they have their own holding-based handlers
    
    def get_animation_frame_index(self) -> int:
        """
        Returns which index to use for the player sprite, based on current situation & gamemode
        
        For cube:
        Every 0.1 seconds that we are in the air, we rotate 22.5 degrees.
        If touching ground, always return 0
        
        For ball:
        Every 0.25s switch the sprite (there are only two)
        
        For ufo:
        same sprite all the time
        
        For wave:
        0 (down) if yvel is negative
        1 (up) if yvel is positive
        2 (flat) if yvel is 0 (on ground, gliding)
        """
        
        match self.gamemode:
            case "cube":
                if not self.in_air:
                    return 0
                seconds_since_last_on_ground = (time_ns() - self.last_on_ground_time) / 1e9
                return int(seconds_since_last_on_ground / 0.1) % 4
            case "ball":
                return int(time() / 0.25) % 2
            
            case "ufo":
                return 0
            
            case "wave":
                if self.yvel < 0:
                    return 0
                elif self.yvel > 0:
                    return 1
                else:
                    return 2
                
            case "ship":
                # this code looks terrible :skull:
                if self.yvel < -EngineConstants.SHIP_TEXTURE_CHANGE_THRESHOLD_2:
                    return 0 # diagonal down
                elif self.yvel < -EngineConstants.SHIP_TEXTURE_CHANGE_THRESHOLD_1:
                    return 1 # semi-down
                elif self.yvel > EngineConstants.SHIP_TEXTURE_CHANGE_THRESHOLD_2:
                    return 4 # up
                elif self.yvel > EngineConstants.SHIP_TEXTURE_CHANGE_THRESHOLD_1:
                    return 3 # flat
                else:
                    return 2
    
    def set_yvel_magnitude(self, strength: float):
        """
        Sets the y velocity to a certain strength, changing direction based on gravity.
        Acts regardless of any other stuff, just straight up sets self.yvel.
        
        (this is because the player can activate orbs while in mid-air, but can't jump normally)
        """
        
        self.yvel = strength * self.sign_of_gravity()
        self.in_air = True # we are PROBABLY in the air. TODO - maybe remove?
        
    def sign_of_gravity(self) -> int:
        """ Returns the sign of the gravity. 1 for normal, -1 for reverse. """
        return 1 if self.gravity > 0 else -1
        
    def normal_gravity(self):
        """ Sets the gravity to normal. """
        self.gravity = EngineConstants.GRAVITY
        
    def reverse_gravity(self):
        """
        Sets the gravity to reverse.
        """
        self.gravity = -EngineConstants.GRAVITY
        
    def change_gravity(self):
        """ Flips the gravity to the negative of what it currently is. """
        self.gravity *= -1
        
    def change_gamemode(self, gamemode: GDConstants.gamemodes):
        """ Change the gamemode of the player, running any associated logic """
        
        if gamemode == "wave":
            self.pos[0] += (1 - EngineConstants.PLAYER_WAVE_HITBOX_X) / 2
            self.pos[1] += (1 - EngineConstants.PLAYER_WAVE_HITBOX_Y) / 2
            
            # add a wave pivot here
            self.create_wave_pivot()
        else:
            self.clear_wave_pivots()
        
        if gamemode == "cube":
            self.jump_requested = False # TEMPORARY FIX 
        
        self.gamemode = gamemode
        
    def change_speed(self, speed: GDConstants.speeds):
        """ Change the speed of the player. """
        self.speed = SPEEDS.decode(speed)
        
    def clear_wave_pivots(self):
        """ Clears the wave pivot points list. """
        self.wave_pivot_points.clear()
        
    def create_wave_pivot(self) -> None:
        """ adds the current player position (center of hitbos) to self.wave_pivot_points """
        
        hb_size = self.get_hitbox_size()
        center_x = self.pos[0] + hb_size[0] / 2
        center_y = self.pos[1] + hb_size[1] / 2        
        
        self.wave_pivot_points.append((center_x, center_y))
        
    def get_hitbox_size(self) -> Tuple[float, float]:
        """
        Returns the hitbox size of the player, as a tuple (x, y).
        """
        match self.gamemode:
            case "wave":
                return EngineConstants.PLAYER_WAVE_HITBOX_X, EngineConstants.PLAYER_WAVE_HITBOX_Y
            case _:
                return EngineConstants.PLAYER_HITBOX_X, EngineConstants.PLAYER_HITBOX_Y