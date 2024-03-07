from engine.collision import Collision
from engine.constants import CONSTANTS
from engine.player import Player
from render.camera import Camera
from render.constants import CameraUtils
from time import time_ns, sleep
from threading import Thread
from math import floor, ceil
from logger import Logger
from typing import List

class Game:
    """
    Represents a level "world" and contains a player object.

    Handles physics ticks for the player and animations
    """

    def __init__(self, leveldata=[]):
        """
        Creates a `Player` object automatically.
        """

        self.leveldata = leveldata or []

        self.player = Player()
        self.camera = Camera(self.leveldata)

        self.running = False
        self.last_tick = None

    def start_level(self, cb=None):
        """
        Begin a separate thread to run level physics/animation ticks
        """

        self.running = True

        # Initialize camera rendering
        self.camera.render_init()
        def render_thread():
            i = 0
            with self.camera.term.hidden_cursor():
                last_frame = time_ns()
                while True:
                    curr_frame = time_ns()

                    self.camera.render(self.player.pos)
                    
                    Logger.log(f"Just rendered frame with player@{[f'{num:2f}' for num in self.player.pos]}. It has been {((curr_frame-last_frame)/1e9):2f}s since last f.")
                    last_frame = curr_frame
                    sleep(1/CameraUtils.RENDER_FRAMERATE)

                    if not self.running:
                        break            

        def physics_thread():
            
            for row in self.leveldata:
                Logger.log(f"Leveldata: {[obj['name'] if obj is not None else 'None' for obj in row]}")
            
            while True:
                
                if not self.running: break
                
                # check collisions
                self.player.curr_collisions = self.generate_collisions_2()

                # apply effects
                for collision in self.player.curr_collisions:                    
                    # don't auto-run effect here if it requires click. That's a job for the key input thread.
                    if not collision.obj.get("requires_click"):
                        self.run_collision_effect(collision)
                
                # after collisions is updated, tick physics.                
                curr_time = time_ns()
                self.player.tick((curr_time - self.last_tick)/1e9)
                self.last_tick = curr_time
                
                # if player's y-pos exceeds camera's ground offset (hit top of screen), crash
                if self.player.pos[1] >= self.camera.ground:
                    self.crash()
                
                # DO NOT REMOVE. removing this slows down the renderer by A LOT
                # even if the physics fps is like 389429 it still speeds things up a lot
                # to have this sleep here. DONT ASK ME WHY IDK EITHER
                sleep(1/CONSTANTS.PHYSICS_FRAMERATE)
        
        self.last_tick = time_ns()
        Thread(target=render_thread).start()
        Thread(target=physics_thread).start()
        
        # Main thread handles key input
        with self.camera.term.cbreak():

            while self.running:
                val = ''
                while val.lower() not in CONSTANTS.ALL_KEYS:
                    val = self.camera.term.inkey(0.01)
                    if not self.running: return

                if val in CONSTANTS.QUIT_KEYS:
                    self.running = False
                    return
                
                elif val in CONSTANTS.JUMP_KEYS:
                    
                    something_got_activated = False
                    
                    # also go through the player's current collisions and
                    # activate the first requires_click effect where "has_been_activated" is False
                    for collision in self.player.curr_collisions:
                        if collision.obj.get("requires_click"):
                            
                            if collision.obj.get("multi_activate"): # always run effect if multi_activate
                                self.run_collision_effect(collision)
                                something_got_activated = True
                                
                            elif not collision.obj.get("has_been_activated"): # run effect if not multi_activate and not activated
                                self.run_collision_effect(collision)
                                something_got_activated = True
                                collision.obj["has_been_activated"] = True
                    
                    Logger.log(f"something_got_activated is {something_got_activated}")
                    # if nothing got activated, then jump
                    if not something_got_activated:
                        self.player.jump()
        
    def run_collision_effect(self, collision: Collision):
        
        # this only checks for crash. Gliding along top/bottom is handled in `Player.tick()`.
        
        # check gravity:
        # If gravity is positive, then "top" is safe, "bottom" crashes.
        # if gravity is negative, then "bottom" is safe, "top" crashes.
        if collision.vert_side is not None:
            if collision.vert_side == "bottom" and self.player.sign_of_gravity() == 1:
                Logger.log("Crashed into top of block.")
                self.crash()
            elif collision.vert_side == "top" and self.player.sign_of_gravity() == -1:
                Logger.log("Crashed into bottom of block.")
                self.crash()
            return # don't run other effects if we are gliding
        
        elif collision.obj["collide_effect"] == 'neg-gravity':
            self.player.gravity = -CONSTANTS.GRAVITY
        elif collision.obj["collide_effect"]  == 'pos-gravity':
            self.player.gravity = CONSTANTS.GRAVITY
        elif collision.obj["collide_effect"]  == 'crash-block':
            Logger.log("Crashed into block.")
            self.crash()
        elif collision.obj["collide_effect"]  == 'crash-spike':
            Logger.log("Crashed into spike.")
            self.crash()
        elif collision.obj["collide_effect"]  == 'yellow-orb':
            Logger.log("Hit yellow orb.")
            self.player.activate_jump_orb(CONSTANTS.PLAYER_JUMP_STRENGTH)
        elif collision.obj["collide_effect"]  == 'purple-orb':
            Logger.log("Hit purple orb.")
            self.player.activate_jump_orb(CONSTANTS.PLAYER_JUMP_STRENGTH*CONSTANTS.PURPLE_ORB_MULTIPLIER)
        elif collision.obj["collide_effect"]  == 'blue-orb':
            Logger.log(f"Hit blue orb. sign of gravity is curr {self.player.sign_of_gravity()} and about to be changed.")
            
            self.player.change_gravity()
            
            # change velocity to a modest amount, in the sign of the NEW direction of gravity
            self.player.yvel = CONSTANTS.BLUE_ORB_STARTING_VELOCITY * self.player.sign_of_gravity()

    def crash(self):
        self.running = False

    def generate_collisions(self) -> list:
        """
        Returns a list of objects that the player is currently touching.
        """

        # TODO - for now, we only search nearby the player, so no large hitboxes yet

        touching = []

        # check the 2x2 lattice cells containing the player's hitbox
        x_range = floor(self.player.pos[0]), ceil(self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X)
        y_range = floor(self.player.pos[1]), ceil(self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y)      
        
        # clip to the leveldata bounds
        y_range = max(y_range[0], 0), min(y_range[1], len(self.leveldata))
        
        #Logger.log(f"Collisions: player is at {self.player.pos[0]:2f}, {self.player.pos[1]:2f}. x_range is {x_range}, y_range is {y_range}.")

        #Logger.log(f"about to enter y loop, range is from {y_range[0]} to {y_range[1]}")
        for y in range(*y_range):
            
            max_x_for_this_row = len(self.leveldata[max(-y-1, -len(self.leveldata))])
            #Logger.log(f"about to enter x loop, range is from max({x_range[0]}, 0) to min({x_range[1]}, {max_x_for_this_row})")
            for x in range(max(x_range[0], 0), min(x_range[1], max_x_for_this_row)):
                # check collisions
                
                # index leveldata with -y-1 because the ground is backward TODO - maybe overhaul system so everything is (0,0) bottom left
                # we also have to clip that y so it doesnt go out of bounds.
                obj = self.leveldata[max(-y-1, -len(self.leveldata))][x]
                
                #Logger.log(f"in both collision loops - obj@[{y}, {x}] is {obj['name'] if obj is not None else 'None'}")
                
                if obj is None: continue

                if obj["hitbox_type"] == "any-touch":

                    # check x collision
                    if (
                    x+obj["hitbox_xrange"][0] < self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X or
                    x+obj["hitbox_xrange"][1] > self.player.pos[0]-CONSTANTS.PLAYER_HITBOX_X):
                        touching.append(Collision(obj))

                    # check y collision
                    elif (
                    y+obj["hitbox_yrange"][0] > self.player.pos[1]-CONSTANTS.PLAYER_HITBOX_Y or
                    y+obj["hitbox_yrange"][1] < self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y):
                        touching.append(Collision(obj))

                elif obj["hitbox_type"] == "solid":

                    # check top - here's how we approach this:
                    # if the player is between the top and the top - constants.solid_surface_leniency,
                    # then we set the player's y (coordinate of bottom side) to the top.
                    # if a player is between bottom and top - constants.solid_surface_leniency, crash
                    
                    Logger.log(f"collisions found solid block. y is {y}, selfplayerpos[1] is {self.player.pos[1]}, objhitboxyrange[0] is {obj['hitbox_yrange'][0]}, objhitboxyrange[1] is {obj['hitbox_yrange'][1]}")
                    
                    if y+obj["hitbox_yrange"][1]-CONSTANTS.SOLID_SURFACE_LENIENCY < self.player.pos[1] <= y+obj["hitbox_yrange"][1]:
                        Logger.log(f">>>>> PLAYER IS ON TOP OF BLOCK. setting _walking_on to {y}+{obj['hitbox_yrange'][1]}")
                        
                        # let player class handle this; see `Player.tick()`
                        # self.player.yvel = 0 # stop falling
                        
                        self.player._walking_on = y+obj["hitbox_yrange"][1]
                        self.player._walking_on_height = CONSTANTS.SOLID_SURFACE_LENIENCY
                        
                        touching.append(Collision(obj, {"is_on_top": True})) 
                        # ^ still add, but the effect checker ignores collisions with top of solids.

                    # check x collision
                    elif (
                        # object's left is less than player's right
                        x+obj["hitbox_xrange"][0] < self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X and
                        # object's right is greater than player's left
                        x+obj["hitbox_xrange"][1] > self.player.pos[0]-CONSTANTS.PLAYER_HITBOX_X):
                        
                        touching.append(Collision(obj))

                    # check y collision ONLY FOR THE BOTTOM SIDE
                    elif (
                        # object's bottom is less than player's top (player went too high)
                        y+obj["hitbox_yrange"][0] < self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y and
                        # player's bottom is less than the object's leniency (player isn't above the block)
                        self.player.pos[1] < y+obj["hitbox_yrange"][1]-CONSTANTS.SOLID_SURFACE_LENIENCY): # player has to be below block
                        
                        touching.append(Collision(obj))
                        
        Logger.log(f"Collisions: player is touching {[collision.obj['name'] if collision is not None else 'None' for collision in touching]}.")
        return touching

    def generate_collisions_2(self) -> List[Collision]:
        """
        Generates a list of `Collision` objects which represents all the objects
        the player's hitbox currently overlaps or is touching.
        """
        
        collisions = []
        
        # Check a 2x2 of lattice cells, centered around the player's hitbox
        x_range = floor(self.player.pos[0]), ceil(self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X)
        y_range = floor(self.player.pos[1]), ceil(self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y)
        
        # clip the y-values to the leveldata bounds. For example, we can't check below index 0 or y>len(leveldata)
        y_range = max(y_range[0], 0), min(y_range[1], len(self.leveldata))
        
        # useful variables
        player_left = self.player.pos[0]
        player_right = self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X
        player_bottom = self.player.pos[1]
        player_top = self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y
        
        #Logger.log(f"Collisions: y_range is {y_range}, x_range is {x_range}.")
        
        for y in range(*y_range):
            # clip x-values based on this row's length (technically all rows should be same len, but just in case)
            curr_x_range = max(x_range[0], 0), min(x_range[1], len(self.leveldata[y]))
            #Logger.log(f"Collisions: Entering xloop for y={y}, updated x_range is {curr_x_range}.")
            for x in range(*curr_x_range):
                
                # weird y-index since levels are 0,0 for bottomleft, and array indices are 0,0 for topleft
                obj = self.leveldata[max(-y-1, -len(self.leveldata))][x] 
                
                #Logger.log(f"Collisions: obj at y={y}, x={x} is {obj['name'] if obj is not None else 'None'}.")
                
                if obj is None: continue
                
                # more useful variables
                obj_left = x+obj["hitbox_xrange"][0]
                obj_right = x+obj["hitbox_xrange"][1]
                obj_bottom = y+obj["hitbox_yrange"][0]
                obj_top = y+obj["hitbox_yrange"][1]
                
                # horiz. collision - for any hitbox type:
                # 1. player's right passed object's left, 
                # 2. but player's left hasn't passed object's right.    
                is_in_horiz_range = player_right > obj_left and player_left < obj_right
                
                #Logger.log(f"   ^^ Its l,r,b,t are {obj_left:.2f},{obj_right:.2f},{obj_bottom:.2f},{obj_top:.2f}. is_in_horiz_range is {is_in_horiz_range}.")
                #Logger.log(f"   ^^ Player info: l,r,b,t are {player_left:.2f},{player_right:.2f},{player_bottom:.2f},{player_top:.2f}.")
                
                if not is_in_horiz_range: continue # ignore if we aren't in horizontal range

                # postcond: we are in the horizontal range of the object
                # thus, if we are also in hostile vertical range, count as a collision.

                if obj["hitbox_type"] == "any-touch":
                    # vert. collision (FOR ANYTOUCH OBJECTS ONLY):
                    # 1. player's top passed object's bottom,
                    # 2. but player's bottom hasn't passed object's top.
                    if player_top > obj_bottom and player_bottom < obj_top:
                        collisions.append(Collision(obj))
                        
                    # else: nothing happens (not in y-range)

                elif obj["hitbox_type"] == "solid":
                    
                    # useful variables
                    object_top_leniency = obj_top-CONSTANTS.SOLID_SURFACE_LENIENCY
                    object_bottom_leniency = obj_bottom+CONSTANTS.SOLID_SURFACE_LENIENCY
                    
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
                    
        return collisions
