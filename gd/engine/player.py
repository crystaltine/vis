from typing import List
from time import time_ns
from copy import deepcopy

from logger import Logger
from engine.constants import CONSTANTS, SPEEDS
from engine.collision import Collision

from engine.gamemodes.cube import tick_cube, jump_cube
from engine.gamemodes.ball import tick_ball, jump_ball
from engine.gamemodes.ufo import tick_ufo, jump_ufo

class Player:
    """
    Represents the player inside a level and handles physics calculations.
    """

    def __init__(self, start_settings: dict = {}):
        """
        (OPTIONAL) `start_settings` format (mainly used for startpos):
        ```python
        {
            pos: [int, int], # [x, y] to start at, default [0, 0]
            speed: "slow", "normal", ... "quadruple" # see constants.SPEEDS
            gravity: int # set a starting gravity. CONSTANTS.gravity for default, negative that for reverse
        }
        ```

        If a setting isn't provided, default values are used,
        which will spawn a cube at [0,0] with regular speed and gravity.
        """
        self.START_SETTINGS = start_settings
        
        self.speed = SPEEDS.decode(start_settings.get("speed")) or SPEEDS.normal
        
        self.gamemode = start_settings.get("gamemode") or "cube"
        """ One of "cube", "ship", "ball", "ufo", "wave", "robot", "spider" (swing maybe? idk)"""
        
        self.ORIGINAL_START_POS = start_settings.get("pos") or [0, 0] # used for resetting
        self.pos = start_settings.get("pos") or [0, 0]
        """ [x, y], where x is horiz (progress). BOTTOM LEFT of player. y=0 means on the ground, and y cannot be negative."""

        self.yvel = 0
        self.gravity = start_settings.get("gravity") or CONSTANTS.GRAVITY
        
        self.jump_requested = False
        """ variable to store when the player jumps before the next physics tick. """

        self.last_on_ground_time = None
        """ Stores the latest time when self.in_air was set to False. Used for calculating cube rotation as we are falling. """
        self.in_air = False
        """ If the player is currently jumping. can't double jump. Jump status is reset to false when the player hits a glidable hitbox. """

        self.curr_collisions: List[Collision] = []
        """ Maintains a list of objects the player is currently touching. Gets updated on every collision check (physics tick)"""

    def tick(self, timedelta: float):
        """ 
        General physics tick for the player. Calls the appropriate tick function based on the current gamemode.
        """
        
        # TODO - make code better by keeping a list and using getattr?
        match self.gamemode:
            case "cube":
                tick_cube(self, timedelta)
            case "ball":
                tick_ball(self, timedelta)
            case "ufo":
                tick_ufo(self, timedelta)
            case _:
                raise Exception(f"[Player/tick] Error: gamemode {self.gamemode} does not exist.")

    
    def reset_physics(self, new_pos = None) -> None:
        """
        Reset to starting physics (yvel=0, in_air=False, etc.)
        This should be used when the player dies or resets.
        Optionally, can select a new position to reset to.
        """
        
        self.pos = new_pos or deepcopy(self.ORIGINAL_START_POS)
        self.in_air = False
        self.yvel = 0
        self.jump_requested = False        
        self.curr_collisions.clear()
        self.gamemode = self.START_SETTINGS.get("gamemode") or "cube"
        self.speed = SPEEDS.decode(self.START_SETTINGS.get("speed")) or SPEEDS.normal
        self.gravity = self.START_SETTINGS.get("gravity") or CONSTANTS.GRAVITY
        self.last_on_ground_time = time_ns()
    
    def jump(self):
        """
        Requests a jump for the next physics tick.
        """
        # NOTE: this is getting moved to each gamemmode's specific jump handler,
        # since you can multi-input in some (such as ufo)
        #if self.in_air: 
        #    #Logger.log(f"XXXXXXXX player tried to jump but cant. pos={self.pos[0]:.2f},{self.pos[1]:.2f}, yvel={self.yvel:.2f}")
        #    return
        
        #Logger.log(f"XXXXXXXX player jumped. pos={self.pos[0]:.2f},{self.pos[1]:.2f}, yvel={self.yvel:.2f}, walking_on={self._walking_on:.2f}, names of colliding objs: {[collision.obj.data['name'] for collision in self.curr_collisions]}")
        
        self.jump_requested = True
    
    def _jump(self):
        """
        Sets the physics for jumping, depending on the gamemode. Should only be used in `Player.tick()`
        and nowhere else. For external use, use `Player.jump()`.
        """
        
        # TODO - make code better by keeping a list and using getattr?
        match self.gamemode:
            case "cube":
                jump_cube(self)
            case "ball":
                jump_ball(self)
            case "ufo":
                jump_ufo(self)
            case _:
                raise Exception(f"[Player/_jump] Error: gamemode {self.gamemode} does not exist.")
    
    def get_animation_frame_index(self) -> int:
        """
        Returns which rotation index to use for the player sprite.
        As of 2:35AM May 29, 2024, 4 different frames are planned:
        - 0: right side up
        - 1: 22.5 degrees
        - 2: 45 degrees
        - 3: 67.5 degrees
        
        NOTE: we are assuming full rotational symmetry here, for simplicity. TODO: support asymmetric icons.
        
        Every 0.1 seconds that we are in the air, we rotate 22.5 degrees.
        If touching ground, always return 0
        """
        
        if not self.in_air:
            return 0
        
        seconds_since_last_on_ground = (time_ns() - self.last_on_ground_time) / 1e9
        
        return int(seconds_since_last_on_ground / 0.1) % 4
    
    def activate_jump_orb(self, strength: float):
        """
        Activates a jump orb. Sets whatever velocity, and sets in_air to true.
        However,this function still has effects when in in_air, unlike regular jumping.
        
        (this is because the player can activate orbs while in mid-air, but can't jump normally)
        
        For yellow orbs, should be ~player jump strength. For purple orbs, should be maybe 0.3*player jump strength?
        For black orbs, should be -4*player jump strength.
        """
        
        self.yvel = strength
        self.in_air = True
        
    def sign_of_gravity(self) -> int:
        """
        Returns the sign of the gravity. 1 for normal, -1 for reverse.
        """
        return 1 if self.gravity > 0 else -1
        
    def normal_gravity(self):
        """
        Sets the gravity to normal.
        """
        self.gravity = CONSTANTS.GRAVITY
        
    def reverse_gravity(self):
        """
        Sets the gravity to reverse.
        """
        self.gravity = -CONSTANTS.GRAVITY
        
    def change_gravity(self):
        """
        Flips the gravity to the negative of what it currently is.
        """
        self.gravity *= -1