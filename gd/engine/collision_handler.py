from typing import List, TYPE_CHECKING
from math import floor, ceil

from engine.constants import EngineConstants
from engine.collision import Collision
from level import LevelObject
from logger import Logger

if TYPE_CHECKING:
    from game import Game

class CollisionHandler:
    """ Handles all collisions-related thingies, this class exists mainly to keep `Game` organized. """
    
    def __init__(self, game: "Game"):
        self.game = game
        
    # IMPORTANT TODO - hitboxes rotate based on object rotation
    def generate_collisions(self) -> List[Collision]:
        """
        Generates a list of `Collision` objects which represents all the objects
        the player's hitbox currently overlaps or is touching.
        """
        
        collisions = []
        
        hitbox_sizes = self.game.player.get_hitbox_size()
        
        # Check a 2x2 of lattice cells, centered around the player's hitbox
        # we pad the positions by 0.25 so when we are at integers, we still check the next block
        x_range = floor(self.game.player.pos[0]-0.25), ceil(self.game.player.pos[0]+hitbox_sizes[0]+0.25)
        y_range = floor(self.game.player.pos[1]-0.25), ceil(self.game.player.pos[1]+hitbox_sizes[1]+0.25)
        
        # clip the y-values to the leveldata bounds. For example, we can't check below index 0 or y>len(leveldata)
        y_range = max(y_range[0], 0), min(y_range[1], self.game.level.height)
        #Logger.log(f"#2^: setting y_range=max({y_range[0]}, 0), min({y_range[1]}, {len(self.game.leveldata)})." )
        
        # useful variables
        player_left = self.game.player.pos[0]
        player_right = self.game.player.pos[0]+hitbox_sizes[0]
        player_bottom = self.game.player.pos[1]
        player_top = self.game.player.pos[1]+hitbox_sizes[1]
        
        #Logger.log(f"Collisions: y_range is {y_range}, x_range is {x_range}.")
        
        for y in range(*y_range):
            # clip x-values based on this row's length (technically all rows should be same len, but just in case)
            curr_x_range = max(x_range[0], 0), min(x_range[1], self.game.level.length)
            #Logger.log(f"Collisions: Entering xloop for y={y}, updated x_range is {curr_x_range}.")
            for x in range(*curr_x_range):
                
                obj = self.game.level.get_object_at(x, y)
                
                if obj is None: continue
                if not obj.data["hitbox_type"]: continue # completely ignore objects with no hitbox type (non-solid objects)
                
                #Logger.log(f"[Game/generate_collisions]: obj at x,y={x},{y} is {obj}. btw, y_range was {y_range} and leveldata has len {len(self.game.leveldata)}")
                #Logger.log(f"^^ Grabbed self.game.leveldata[{max(len(self.game.leveldata)-y-1, 0)}][{x}]")
                
                # more useful variables
                obj_left = x+obj.data["hitbox_xrange"][0]
                obj_right = x+obj.data["hitbox_xrange"][1]
                obj_bottom = y+obj.data["hitbox_yrange"][0]
                obj_top = y+obj.data["hitbox_yrange"][1]
                
                # horiz. collision - for any hitbox type:
                # 1. player's right passed object's left, 
                # 2. but player's left hasn't passed object's right.    
                is_in_horiz_range = player_right > obj_left and player_left < obj_right
                
                #Logger.log(f"   ^^ Its l,r,b,t are {obj_left:.2f},{obj_right:.2f},{obj_bottom:.2f},{obj_top:.2f}. is_in_horiz_range is {is_in_horiz_range}.")
                #Logger.log(f"   ^^ Player info: l,r,b,t are {player_left:.2f},{player_right:.2f},{player_bottom:.2f},{player_top:.2f}.")
                
                if not is_in_horiz_range: continue # ignore if we aren't in horizontal range

                # postcond: we are in the horizontal range of the object
                # thus, if we are also in hostile vertical range, count as a collision.

                if obj.data["hitbox_type"] == "any-touch":
                    # vert. collision (FOR ANYTOUCH OBJECTS ONLY):
                    # 1. player's top passed object's bottom,
                    # 2. but player's bottom hasn't passed object's top.
                    if player_top > obj_bottom and player_bottom < obj_top:
                        collisions.append(Collision(obj))
                        
                    # else: nothing happens (not in y-range)

                elif obj.data["hitbox_type"] == "solid":
                    
                    # useful variables
                    object_top_leniency = obj_top-EngineConstants.SOLID_SURFACE_LENIENCY
                    object_bottom_leniency = obj_bottom+EngineConstants.SOLID_SURFACE_LENIENCY
                    
                    # vert. collision (FOR SOLID OBJECTS ONLY):
                    # - if player's bottom is in the range [object_top - leniency, object_top]
                    #   ^ then we count this as a "top" collision
                    # - if player's top is in the range [object_bottom, object_bottom + leniency]
                    #   ^ then we count this as a "bottom" collision 
                    # - if either the player's bottom or top are between:
                    #    * its leniency range and...
                    #    * the opposite side, THEN: count as reg. collution
                    #
                    # these SHOUld be mutually exclusive ranges (cant be both at once)
                    
                    #Logger.log(f"   cond1: {object_top_leniency:.2f} < {player_bottom:.2f} <= {obj_top:.2f}")
                    #Logger.log(f"   cond2: {obj_bottom:.2f} <= {player_top:.2f} < {object_bottom_leniency:.2f}")
                    #Logger.log(f"   cond3: {object_bottom_leniency:.2f} < {player_top:.2f} < {obj_top:.2f}")
                    
                    if object_top_leniency < player_bottom <= obj_top:
                        collisions.append(Collision(obj, "top", obj_top))
                    
                    elif obj_bottom <= player_top < object_bottom_leniency:
                        collisions.append(Collision(obj, "bottom", obj_bottom))
                        
                    elif object_bottom_leniency <= player_top <= obj_top or obj_bottom <= player_bottom <= object_top_leniency:
                        collisions.append(Collision(obj))

                    # else: nothing happens (not in y-range)
        
        #Logger.log(f"Collisions END: player is touching {[(collision.obj.data['name'],collision.vert_side,collision.vert_coord) if collision is not None else 'None' for collision in collisions]}.")
        return collisions

    def run_collision_effect(self, collision: Collision):
        """ Applies the actual effect of `collision` onto the player """
            
        # this only checks for crash. Gliding along top/bottom is handled in `Player.tick()`.
        
        # check gravity:
        # If gravity is positive(down), but we are moving up, "bottom" crashes. (we jumped into a block.)
        # if gravity is negative(up), but we are moving down, "top" crashes. (we jumped into a block.)
        if collision.vert_side is not None:
            if collision.vert_side == "bottom" and self.game.player.sign_of_gravity() == 1 and self.game.player.yvel > 0:
                Logger.log("Crashed into top of block.")
                self.game.crash_normal()
            elif collision.vert_side == "top" and self.game.player.sign_of_gravity() == -1 and self.game.player.yvel < 0:
                Logger.log("Crashed into bottom of block.")
                self.game.crash_normal()
            return # don't run other effects if we are gliding
        
        effect: str = collision.obj.data["collide_effect"]
        
        if effect == "gravity-normal":
            self.game.player.normal_gravity()
        elif effect == "gravity-reverse":
            self.game.player.reverse_gravity()
            
        elif effect == 'crash-block':
            self.game.crash_normal()
        elif effect == 'crash-obstacle':
            self.game.crash_normal()
            
        elif effect == 'yellow-orb':
            self.game.player.set_yvel_magnitude(EngineConstants.PLAYER_JUMP_STRENGTH*EngineConstants.YELLOW_ORB_MULTIPLIER)
        elif effect == 'yellow-pad':
            self.game.player.set_yvel_magnitude(EngineConstants.PLAYER_JUMP_STRENGTH*EngineConstants.YELLOW_PAD_MULTIPLIER)
        elif effect == 'purple-orb':
            self.game.player.set_yvel_magnitude(EngineConstants.PLAYER_JUMP_STRENGTH*EngineConstants.PURPLE_ORB_MULTIPLIER)
        elif effect == 'purple-pad':
            self.game.player.set_yvel_magnitude(EngineConstants.PLAYER_JUMP_STRENGTH*EngineConstants.PURPLE_PAD_MULTIPLIER)
        elif effect == 'red-orb':
            self.game.player.set_yvel_magnitude(EngineConstants.PLAYER_JUMP_STRENGTH*EngineConstants.RED_ORB_MULTIPLIER)
        elif effect == 'red-pad':
            self.game.player.set_yvel_magnitude(EngineConstants.PLAYER_JUMP_STRENGTH*EngineConstants.RED_PAD_MULTIPLIER)
        elif effect in ['blue-orb', 'blue-pad']:
            self.game.player.yvel = EngineConstants.BLUE_ORB_STARTING_VELOCITY * -self.game.player.sign_of_gravity()
            self.game.player.change_gravity()
        elif effect == 'green-orb':
            self.game.player.change_gravity()
            self.game.player.set_yvel_magnitude(EngineConstants.PLAYER_JUMP_STRENGTH*EngineConstants.YELLOW_ORB_MULTIPLIER)
        elif effect == 'black-orb':
            self.game.player.yvel = EngineConstants.BLACK_ORB_VELOCITY * self.game.player.sign_of_gravity()
        
        elif effect.startswith("gamemode-"):
            gamemode = effect[9:]
            self.game.player.change_gamemode(gamemode)
            Logger.log(f"set player gameode to {gamemode}.")
        
        elif effect.startswith("speed-"):
            gamemode = effect[6:]
            self.game.player.change_speed(gamemode)

    def highest_solid_object_beneath_player(self, timedelta: float) -> "LevelObject | None":
        """
        Returns the highest solid object beneath the player (y value is less).
        
        Only searches a distance of ceil(abs(player yvel)) beneath the player
        in order to not search the entire column (this requires that the game run >1fps for it to work properly)
        
        Solid is defined as objects whose crash_effect is `"crash-block"` (so for now, just blocks) 
        
        If the player is in between two "columns" of the level (say, at `(x,y)=(4.5,10)`), then attempts to return the
        higher block (e.g. if the highest block at x=4 is at y=6, and the highest block at x=5 is at y=7, this function
        will return the block at x=5, y=7). (IF IN RANGE)
        
        However, if the highest blocks under the player are at the same height, then it will return leftmost block (lower x-val)  
        
        Returns None if nothing in range.
        """
        
        # scan the two columns the player might be occupying
        
        # calc. boundaries of check
        left = floor(self.game.player.pos[0])
        right = ceil(self.game.player.pos[0]+self.game.player.get_hitbox_size()[0])
        
        top = floor(self.game.player.pos[1]) - 1 # only check BELOW the player
        
        # check ceil(player yvel) blocks below/above the player
        # ^ this is so we dont check a huge number of blocks - we are assuming the game is running faster than 1fps lol
        
        num_rows_to_check = ceil(abs(self.game.player.yvel) * timedelta)
        
        Logger.log(f"highest solid obj: player pos is {self.game.player.pos[0]:2f},{self.game.player.pos[1]:2f}, left->right is {left}->{right}, top is {top}, num_rows_to_check is {num_rows_to_check}.")
        
        for x in range(left, right+1):
            for y in range(top, max(-1, top-num_rows_to_check-1), -1):
                if (obj := self.game.level.get_object_at(x, y)) is not None:
                    if obj.data.get("hitbox_type") == "solid":
                        return obj # return first SOLID object we find (since it is leftmost and highest)
        
        return None
    
    def lowest_solid_object_above_player(self, timedelta: float) -> "LevelObject | None":
        """
        Returns the lowest solid object above the player (y value is more than player-top).
        
        Only searches a distance of ceil(abs(player yvel)) above the player
        in order to not search the entire column (this requires that the game run >1fps for it to work properly)
        
        Solid is defined as objects whose crash_effect is `"crash-block"` (so for now, just blocks) 
        
        If the player is in between two "columns" of the level (say, at `(x,y)=(4.5,9.5)`), then attempts to return the
        higher block (e.g. if the lowest block at x=4 is at y=11, and the lowest block at x=5 is at y=10, this function
        will return the block at x=4, y=11) (x=5 block is not in range, since player top is at 9.5 + 1 (assuming 1-block height),
        and y=10 is not above the player)). (IF IN RANGE)
        
        However, if the lowest blocks above the player are at the same height, then it will return leftmost block (lower x-val)  
        
        Returns None if nothing in range.
        """
        
        # scan the two columns the player might be occupying
        
        # calc. boundaries of check
        left = floor(self.game.player.pos[0])
        right = ceil(self.game.player.pos[0]+self.game.player.get_hitbox_size()[0])
        
        bottom = ceil(self.game.player.pos[1] + 1) # only check ABOVE THE TOP of the player
        
        # check ceil(player yvel) blocks below/above the player
        # ^ this is so we dont check a huge number of blocks - we are assuming the game is running faster than 1fps lol
        
        num_rows_to_check = ceil(abs(self.game.player.yvel) * timedelta)
        
        for x in range(left, right+1):
            for y in range(bottom, bottom+num_rows_to_check+1):
                if (obj := self.game.level.get_object_at(x, y)) is not None:
                    if obj.data.get("hitbox_type") == "solid":
                        return obj # return first SOLID object we find 
        
        return None
    