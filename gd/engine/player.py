from engine.constants import CONSTANTS, SPEEDS
from logger import Logger
from typing import List
from engine.collision import Collision

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
        self.speed = SPEEDS.decode(start_settings.get("speed")) or SPEEDS.normal
        self.pos = start_settings.get("pos") or [10, 0]
        """ [x, y], where x is horiz (progress). BOTTOM LEFT of player. """

        self.yvel = 0
        self.gravity = start_settings.get("gravity") or CONSTANTS.GRAVITY
        
        self._jump_requested = False
        """ variable to store when the player jumps before the next physics tick. """

        self.mid_jump = False
        """ If the player is currently jumping. can't double jump. Jump status is reset to false when the player hits a glidable hitbox. """

        self.curr_collisions: List[Collision] = []
        """ Maintains a list of objects the player is currently touching. Gets updated on every collision check (physics tick)"""

    def tick(self, timedelta: float):
        """ 
        Physics tick for the player.

        Note Mar. 7, 2024 @2:14AM: this currently runs AFTER collisions are checked for the current position.

        Timedelta should be in seconds and should represent the time since last tick.
        If this is the first tick, then timedelta should be 0 (i think).
        """
        
        Logger.log(f"Tick: td={timedelta}, pos={self.pos[0]:.2f},{self.pos[1]:.2f}, yvel={self.yvel:.2f}, jump_req={self._jump_requested}, mid_jump={self.mid_jump}, grav_dir={self.gravity}")
        Logger.log(f"^^^: collisions: {[(collision.obj.data['name'], collision.vert_coord, collision.vert_side) for collision in self.curr_collisions]}")
        
        # always move right no matter what
        self.pos[0] += self.speed * CONSTANTS.BLOCKS_PER_SECOND * timedelta
        
        # GLIDE HANDLING BELOW (setting y-values)
        
        # if y < 0, then we just hit ground and should just set y=0, yvel=0, mid_jump=False
        if self.pos[1] <= 0 and self.yvel <= 0: # if we are going up, we shouldnt hit the ground
            Logger.log(f"Hit ground. setting y-pos to 0 and mid_jump to False")
            self.pos[1] = 0
            self.yvel = 0
            self.mid_jump = False            
        
        # if gravity is + (down) and we have a "top" collision, adjust the y position to be on top of the block
        elif (self.gravity > 0 and any(collision.vert_side == "top" for collision in self.curr_collisions)):
            if self.yvel < 0: # only hit ground if we are going down
                self.pos[1] = max([collision.vert_coord for collision in self.curr_collisions if collision.vert_side == "top"])
                self.yvel = 0
                
                Logger.log(f"reg gravity: setting y-pos to {self.pos[1]:.2f} and mid_jump to False")
                self.mid_jump = False
        
        # if gravity is - (up) and we have a "bottom" collision, adjust the y position to be on top of the block
        elif (self.gravity < 0 and any(collision.vert_side == "bottom" for collision in self.curr_collisions)):
            if self.yvel > 0: # only hit ground if we are going up
                # we have to subtract the player hitbox yrange to get the top of the player
                self.pos[1] = min([collision.vert_coord for collision in self.curr_collisions if collision.vert_side == "bottom"])-CONSTANTS.PLAYER_HITBOX_Y
                self.yvel = 0
                
                Logger.log(f"rev gravity: setting y-pos to {self.pos[1]:.2f} and mid_jump to False")
                self.mid_jump = False
        
        # otherwise are in mid-air and should apply gravity
        else:
            Logger.log(f"seems like we are in the air, mid_jump -> true after this.")
            self.mid_jump = True
            self.yvel -= self.gravity * timedelta
            self.yvel = max(min(self.yvel, CONSTANTS.TERMINAL_VEL), -CONSTANTS.TERMINAL_VEL) # clamp yvel to terminal velocity
        
        # if jump was requested, set the jump physics
        if self._jump_requested:
            self._jump()
            self._jump_requested = False
        
        Logger.log(f"End of tick: updating pos[1] to {self.pos[1]:.4f} since yvel={self.yvel:.4f} and timedelta={timedelta:.4f}")
        self.pos[1] += self.yvel * timedelta
        
    def jump(self):
        """
        Requests a jump for the next physics tick.
        """
        if self.mid_jump: 
            Logger.log(f"XXXXXXXX player tried to jump but cant. pos={self.pos[0]:.2f},{self.pos[1]:.2f}, yvel={self.yvel:.2f}")
            return
        
        #Logger.log(f"XXXXXXXX player jumped. pos={self.pos[0]:.2f},{self.pos[1]:.2f}, yvel={self.yvel:.2f}, walking_on={self._walking_on:.2f}, names of colliding objs: {[collision.obj.data['name'] for collision in self.curr_collisions]}")
        
        self._jump_requested = True
    
    def _jump(self):
        """
        Sets the physics for jumping. Should only be used in `Player.tick()`
        and nowhere else. For external use, use `Player.jump()`.
        """
        self.yvel = CONSTANTS.PLAYER_JUMP_STRENGTH * self.sign_of_gravity()
        self.mid_jump = True
    
    def activate_jump_orb(self, strength: float):
        """
        Activates a jump orb. Sets whatever velocity, and sets mid_jump to true.
        However,this function still has effects when in mid_jump, unlike regular jumping.
        
        (this is because the player can activate orbs while in mid-air, but can't jump normally)
        
        For yellow orbs, should be ~player jump strength. For purple orbs, should be maybe 0.3*player jump strength?
        For black orbs, should be -4*player jump strength.
        """
        
        self.yvel = strength
        self.mid_jump = True
        
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