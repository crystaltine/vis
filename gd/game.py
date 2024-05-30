from engine.collision import Collision
from engine.constants import CONSTANTS
from engine.player import Player
from render.camera import Camera
from render.constants import CameraUtils
from time import time_ns, sleep
from threading import Thread
from math import floor, ceil
from logger import Logger
from typing import List, TYPE_CHECKING
import traceback
from copy import deepcopy
from multiprocessing import process
from copy import deepcopy
from draw_utils import Position
from img2term.main import draw
from bottom_menu import draw_text
import time

if TYPE_CHECKING:
    from engine.objects import LevelObject

class Game:
    """
    Represents a level "world" and contains a player object.

    Handles physics ticks for the player and animations
    """

    def __init__(self, leveldata: List[List['LevelObject']] = []):
        """
        Creates a `Player` object automatically.
        """

        self.leveldata = leveldata

        self.player = Player()
        self.camera = Camera(self.leveldata)

        self.is_crashed = False
        self.running = False
        self.last_tick = None

        # wayyy too many of these variables, don't need them all - will come back later and clean this up
        self.paused = False
        self.exiting = False
        self.reseting = False
        self.practice_mode = False
        self.last_checkpoint = None
        self.checkpoints = []
        self.attempt_number = 1
        self.game_start_time = time.time()

    def start_level(self, cb=None):
        """
        Begin a separate thread to run level physics/animation ticks
        """

        self.running = True
        self.paused = False
        
        self.camera.render_init()
        def render_thread():
            try:
                last_frame = time_ns()
                while True:
                    curr_frame = time_ns()

                    fps_str = f"{(1e9/(curr_frame-last_frame)):2f}" if (curr_frame-last_frame != 0) else "inf"
                    Logger.log(f"[Game/render_thread] Rendering frame, player@{[f'{num:2f}' for num in self.player.pos]}. FPS: {fps_str}")
                    self.camera.render(self)
                    # renders the most recent checkpoint if it exists
                    # note: this has been moved to Camera.render
                    # if self.last_checkpoint:
                    #     self.camera.draw_checkpoint(self.player.pos[0], self.last_checkpoint[0], self.last_checkpoint[1])
                    
                    #Logger.log(f"Just rendered frame with player@{[f'{num:2f}' for num in self.player.pos]}. It has been {((curr_frame-last_frame)/1e9):2f}s since last f.")
                    last_frame = curr_frame

                    # draws the attempt number given the players current and intial positions
                    sleep(1/CameraUtils.RENDER_FRAMERATE)

                    if not self.running:
                        break     
            except Exception as e:
                Logger.log(f"[Render Thread] ERROR: {traceback.format_exc()}")
                self.running = False       

        def physics_thread():
            try:
                while True:
                    #Logger.log(f"running physics tick. player pos is {self.player.pos[0]:.2f},{self.player.pos[1]:.2f}, time_ns is {time_ns()}")
                    if not self.running: break
                    
                    # before collisions is updated, tick physics.                
                    curr_time = time_ns()
                    self.player.tick((curr_time - self.last_tick)/1e9)
                    Logger.log(f"[Physics Thread] Player ticked. pos={self.player.pos[0]:.2f},{self.player.pos[1]:.2f}, yvel={self.player.yvel:.2f}, TPS: {1/((curr_time-self.last_tick)/1e9):.2f}")
                    self.last_tick = curr_time
                    
                    # check collisions
                    self.player.curr_collisions = self.generate_collisions()
                    
                    # apply collision effects
                    for collision in self.player.curr_collisions:                    
                        # don't auto-run effect here if it requires click. That's a job for the key input thread.
                        Logger.log(f"Running collision effect for: {collision}")
                        if not collision.obj.data.get("requires_click"):
                            self.run_collision_effect(collision)
                    
                    # DO NOT REMOVE. removing this slows down the renderer by A LOT
                    # even if the physics fps is like 389429 it still speeds things up a lot
                    # to have this sleep here. DONT ASK ME WHY IDK EITHER
                    sleep(1/CONSTANTS.PHYSICS_FRAMERATE)
            except Exception as e:
                Logger.log(f"[Physics Thread] ERROR: {traceback.format_exc()}")
                self.running = False
        
        self.last_tick = time_ns()
        Thread(target=render_thread).start()
        Thread(target=physics_thread).start()
        # stores the start time of the level (for assigning checkpoint purposes)
        start_time = time.time()
        
        # Main thread handles key input
        with self.camera.term.cbreak():

            while self.running:
                # val = ''
                # while val.lower() not in CONSTANTS.ALL_KEYS:
                val = self.camera.term.inkey(0.01)
                if not self.running:
                    return
                # if a checkpoint has not been set for 2 seconds, set one at the players current position
                if time.time() - start_time > 2 and self.practice_mode:
                    self.last_checkpoint = deepcopy(self.player.pos)
                    self.checkpoints.append((self.last_checkpoint[0], self.last_checkpoint[1]))
                    # reset the timer
                    start_time = time.time()

                if val in CONSTANTS.ALL_KEYS:
                    if val in CONSTANTS.QUIT_KEYS:
                        self.running = False
                        return
                    elif val in CONSTANTS.PAUSE_KEYS:
                        self.pause()
                        return
                    # place a checkpoint if a user attempts to
                    elif val in CONSTANTS.CHECKPOINT_KEYS and self.practice_mode:
                        self.last_checkpoint = deepcopy(self.player.pos)
                        self.checkpoints.append((self.last_checkpoint[0], self.last_checkpoint[1]))
                        # reset the checkpoint timer
                        start_time = time.time()
                    # remove the most recent checkpoint if a user attempts to
                    elif val in CONSTANTS.REMOVE_CHECKPOINT_KEYS and self.practice_mode and self.checkpoints:
                        self.checkpoints.pop()
                        self.last_checkpoint = self.checkpoints[-1] if self.checkpoints else None
                        # reset the checkpoint timer
                        start_time = time.time()
                    elif val in CONSTANTS.JUMP_KEYS:
                        
                        something_got_activated = False
                        
                        # also go through the player's current collisions and
                        # activate the first requires_click effect where "has_been_activated" is False
                        for collision in self.player.curr_collisions:
                            if collision.obj.data.get("requires_click"):
                                
                                if collision.obj.data.get("multi_activate"): # always run effect if multi_activate
                                    self.run_collision_effect(collision)
                                    something_got_activated = True
                                    break # can only perform one action per jump
                                    
                                elif not collision.has_been_activated: # run effect if not multi_activate and not activated
                                    self.run_collision_effect(collision)
                                    something_got_activated = True
                                    collision.has_been_activated = True
                                    break # can only perform one action per jump
                        
                        Logger.log(f"something_got_activated is {something_got_activated}")
                        # if nothing got activated, then jump
                        if not something_got_activated:
                            self.player.jump()
        
    def run_collision_effect(self, collision: Collision):
        
        # this only checks for crash. Gliding along top/bottom is handled in `Player.tick()`.
        
        # check gravity:
        # If gravity is positive(down), but we are moving up, "bottom" crashes. (we jumped into a block.)
        # if gravity is negative(up), but we are moving down, "top" crashes. (we jumped into a block.)
        if collision.vert_side is not None:
            if collision.vert_side == "bottom" and self.player.sign_of_gravity() == 1 and self.player.yvel > 0:
                Logger.log("Crashed into top of block.")
                self.crash_normal()
            elif collision.vert_side == "top" and self.player.sign_of_gravity() == -1 and self.player.yvel < 0:
                Logger.log("Crashed into bottom of block.")
                self.crash_normal()
            return # don't run other effects if we are gliding
        
        elif collision.obj.data["collide_effect"] == 'neg-gravity':
            self.player.gravity = -CONSTANTS.GRAVITY
        elif collision.obj.data["collide_effect"]  == 'pos-gravity':
            self.player.gravity = CONSTANTS.GRAVITY
        elif collision.obj.data["collide_effect"]  == 'crash-block':
            Logger.log("Crashed into block")
            self.crash_normal()
        elif collision.obj.data["collide_effect"]  == 'crash-spike':
            Logger.log(f"Crashed into spike, spike x is {collision.obj.x}, player x is {self.player.pos[0]}")
            self.crash_normal()
        elif collision.obj.data["collide_effect"]  == 'yellow-orb':
            Logger.log("Hit yellow orb.")
            self.player.activate_jump_orb(CONSTANTS.PLAYER_JUMP_STRENGTH)
        elif collision.obj.data["collide_effect"]  == 'purple-orb':
            Logger.log("Hit purple orb.")
            self.player.activate_jump_orb(CONSTANTS.PLAYER_JUMP_STRENGTH*CONSTANTS.PURPLE_ORB_MULTIPLIER)
        elif collision.obj.data["collide_effect"]  == 'blue-orb':
            Logger.log(f"Hit blue orb. sign of gravity is curr {self.player.sign_of_gravity()} and about to be changed.")
            
            self.player.change_gravity()
            
            # change velocity to a modest amount, in the sign of the NEW direction of gravity
            self.player.yvel = CONSTANTS.BLUE_ORB_STARTING_VELOCITY * -self.player.sign_of_gravity()

    def crash_normal(self, restart: bool = True):
        """
        The old function for crash handling. Might convert to normal mode crash later on.
        """
        self.is_crashed = True
        #self.running=True
        # self.player=Player()
        #self.start_level()
        #self.running = False
        if not restart:
            self.running = False
            return

        sleep(CONSTANTS.COOLDOWN_BETWEEN_ATTEMPTS)
        self.is_crashed = False
        self.player.reset_physics()
        self.last_tick = time_ns() # this is to prevent moving forward while we are dead lol

        # otherwise, restart the level by setting pos back to beginning 
        # also, NOTE: reset song if that is implemented
        Logger.log(f"crash_normal(): setting player pos back to {self.player.ORIGINAL_START_POS}")
        self.attempt_number += 1

    def pause(self) -> None:
        """
        Pauses the game and displays the pause menu.
        Draws the pause menu background, progress bar, and pause menu buttons. 
        Then passes off handling user interaction with the pause menu.
        Also sets initial selected index to the play button.
        """
        # stops the game and sets paused to true
        self.running = False
        self.paused = True
        # calculates progress bar based on length of level and player position
        progresspercent = round((self.player.pos[0] / len(self.leveldata[0])) * 100)
        # sets selected index to play button
        pausemenuselectindex = 1

        # Draw pause menu background, progress bar, and buttons
        draw('assets/pausemenubg.png', Position.Relative(top=5, left=10), (self.camera.term.width - 20, self.camera.term.height * 2 - 20), 'scale')
        draw_text(f"Progress: {progresspercent}%", (self.camera.term.width - 10) // 2, 10, bg_color='black')
        self.draw_pause_menu_buttons(pausemenuselectindex)

        # call method to handle interaction with pause menu
        self.handle_pause_menu_interaction(pausemenuselectindex)

    def handle_pause_menu_interaction(self, pausemenuselectindex: int) -> None:
        """
        Handles the user interaction with the pause menu.
        Processes user input to navigate the pause menu and perform actions
        such as reset, unpause, toggle practice mode, or exit.
        Args:
            pausemenuselectindex (int): The current selected index in the pause menu.
        """
        reset = False
        unpause = False

        while not self.running:
            with self.camera.term.cbreak():
                val = self.camera.term.inkey(1)
                changed = False

                if val:
                    # move the selected index
                    if val.name == 'KEY_LEFT':
                        changed = True
                        pausemenuselectindex -= 1
                        if pausemenuselectindex < 0:
                            pausemenuselectindex = 3
                    # move the selected index
                    elif val.name == 'KEY_RIGHT':
                        changed = True
                        pausemenuselectindex += 1
                        if pausemenuselectindex > 3:
                            pausemenuselectindex = 0
                    # carry out functions based on selected index if enter is pressed, then break
                    # out of the while loop
                    elif val.name == 'KEY_ENTER':
                        if pausemenuselectindex == 0:
                            reset = True
                        elif pausemenuselectindex == 1:
                            unpause = True
                        elif pausemenuselectindex == 2:
                            self.practice_mode = not self.practice_mode
                            reset = True
                        elif pausemenuselectindex == 3:
                            self.exiting = True
                        break

                    # if the selected element is changed, redraw the pause buttons accordingly
                    if changed:
                        self.draw_pause_menu_buttons(pausemenuselectindex)

        if reset:
            self.reset()
        elif unpause:
            self.unpause()

    def draw_pause_menu_buttons(self, index: int) -> None:
        """
        Draws the pause menu buttons with highlights based on the selected index.
        Args:
            index (int): The index of the currently selected menu button.
        """

        # OLD TEXT BASED RENDERING OF BUTTONS
        # draw_text("Reset", 10 + ((self.camera.term.width - 50) // 4), (self.camera.term.height) // 2, bg_color='white' if index == 0 else 'black')
        # draw_text("Play", 10 + ((self.camera.term.width - 50) // 4) * 2, (self.camera.term.height) // 2, bg_color='white' if index == 1 else 'black')
        # draw_text("Practice", 10 + ((self.camera.term.width - 50) // 4) * 3, (self.camera.term.height) // 2, bg_color=practice_bg_color)
        # draw_text("Exit", 10 + ((self.camera.term.width - 50) // 4) * 4, (self.camera.term.height) // 2, bg_color='white' if index == 3 else 'black')


        # Stores the positions and labels for the buttons
        positions = [
            "calc(15% - 10ch)",
            "calc(36.5% - 10ch)",
            "calc(58% - 10ch)",
            "calc(79.5% - 10ch)"
        ]
        button_labels = ["reset_button", "play_button", "practice_button", "exit_button"]

        # Determine the practice button state
        practice_bg_color = '_active' if self.practice_mode else ''

        # Draw each button, highlighting the selected one
        for i, label in enumerate(button_labels):
            selected = '_selected' if index == i else ''
            suffix = practice_bg_color if label == "practice_button" and not selected else selected
            draw(f"assets/pause_menu/{label}{suffix}.png", pos=Position.Relative(left=positions[i], bottom="calc(55% - 10ch)"))

        # Draw additional text labels for controls
        draw_text("Add Checkpoint - Z", 12 + ((self.camera.term.width - 64) // 4) * 3, (self.camera.term.height + 20) // 2, bg_color='black')
        draw_text("Remove Checkpoint - X", 10 + ((self.camera.term.width - 64) // 4) * 3, (self.camera.term.height + 25) // 2, bg_color='black')

    def unpause(self) -> None:
        """
            Unpauses the level.
        """
        self.start_level()
        self.paused = False

    def crash(self) -> None:
        """
        Handles the game crash event.
        First, stops the game. If the played died within 0.4 seconds of starting and
        is in practice mode, it removes the last checkpoint assuming it will lead
        to an infinite death loop. Finally, it then resets the game.
        """
        self.running = False

        if time.time() - self.game_start_time < 0.4 and self.practice_mode and self.checkpoints:
            self.checkpoints.pop()
            self.last_checkpoint = self.checkpoints[-1] if self.checkpoints else None

        self.reset()

    def reset(self) -> None:
        """
        Resets the level.
        """
        self.reseting = True

        # OLD RESET CODE - ATTEMPT TO TERMINATE THE THREADS FAILED MISERABLY
        # self.running = False
        # self.paused = False
        # # self.terminate_threads = True  # Set the flag to terminate threads

        # # # Wait for the render and physics threads to finish
        # # if self.render_thread_instance:
        # #     self.render_thread_instance.join()
        # # if self.physics_thread_instance:
        # #     self.physics_thread_instance.join()

        # # self.terminate_threads = False
        # self.player = Player()
        # self.camera = Camera(self.leveldata)
        # self.last_tick = None
        # self.start_level()

    def generate_collisions(self) -> List[Collision]:
        """
        Generates a list of `Collision` objects which represents all the objects
        the player's hitbox currently overlaps or is touching.
        """
        
        collisions = []
        #Logger.log(f"----- New collision generation, using playerpos={self.player.pos[0]:.2f},{self.player.pos[1]:.2f}")
        
        # Check a 2x2 of lattice cells, centered around the player's hitbox
        # we pad the positions by 0.25 so when we are at integers, we still check the next block
        x_range = floor(self.player.pos[0]-0.25), ceil(self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X+0.25)
        y_range = floor(self.player.pos[1]-0.25), ceil(self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y+0.25)
        
        # clip the y-values to the leveldata bounds. For example, we can't check below index 0 or y>len(leveldata)
        y_range = max(y_range[0], 0), min(y_range[1], len(self.leveldata))
        #Logger.log(f"#2^: setting y_range=max({y_range[0]}, 0), min({y_range[1]}, {len(self.leveldata)})." )
        
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
                obj = self.leveldata[max(len(self.leveldata)-y-1, 0)][x]
                
                #Logger.log(f"[Game/generate_collisions]: obj at x,y={x},{y} is {obj}. btw, y_range was {y_range} and leveldata has len {len(self.leveldata)}")
                #Logger.log(f"^^ Grabbed self.leveldata[{max(len(self.leveldata)-y-1, 0)}][{x}]")
                
                if obj.data is None: continue
                
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
        
        #Logger.log(f"Collisions END: player is touching {[(collision.obj.data['name'],collision.vert_side,collision.vert_coord) if collision is not None else 'None' for collision in collisions]}.")
        return collisions
