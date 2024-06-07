from copy import deepcopy
from time import time_ns, sleep
from threading import Thread
from copy import deepcopy
import traceback
import time

from logger import Logger
from render.camera import Camera
from render.constants import CameraConstants
from engine.constants import EngineConstants
from engine.player import Player
from engine.collision_handler import CollisionHandler
from draw_utils import Position
from img2term.main import draw
from bottom_menu import draw_text
from level import Level
from keyboard.keyboard_listener import KeyboardListener
from keyboard.key_event import KeyEvent
from practice_mode import PracticeMode

class Game:
    """
    Represents a level "world" and contains a player object.

    Coordinates keyboard, render, physics threads. 
    """

    def __init__(self, level: Level):
        self.level = level

        self.player = Player()
        self.camera = Camera(self.level)
        self.collision_handler = CollisionHandler(self)

        self.is_crashed = False
        self.running = False
        self.last_tick = None
        
        self.activated_objects = []
        """ Stores which objects had their activated properties set to true, so we can reset them on crash. """

        self.paused = False #currently unused variable
        self.exiting = False
        self.practice_mode = False
        # creating object that will handle practice mode functionality
        self.practicemodeobj = PracticeMode(self)
        self.last_checkpoint = None
        self.checkpoints = []
        self.attempt_number = 1
        self.game_start_time = time.time()

    def start_level(self) -> None:
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
                    if self.is_crashed:
                        Logger.log(f"[Game/render_thread] Rendering CRASHED frame, player@{[f'{num:2f}' for num in self.player.pos]}. FPS: {fps_str}")
                    else:
                        Logger.log(f"[Game/render_thread] Rendering LIVE frame, player@{[f'{num:2f}' for num in self.player.pos]}. FPS: {fps_str}")
                    
                    # adds a checkpoint if its been over 2 seconds since the last checkpoint was added
                    if self.practice_mode and self.practicemodeobj.is_checkpoint_time_over():
                        self.practicemodeobj.add_checkpoint(self.player.pos)

                    self.camera.render(self)
                    # renders the most recent checkpoint if it exists
                    # note: this has been moved to Camera.render
                    # if self.last_checkpoint:
                    #     self.camera.draw_checkpoint(self.player.pos[0], self.last_checkpoint[0], self.last_checkpoint[1])
                    
                    #Logger.log(f"Just rendered frame with player@{[f'{num:2f}' for num in self.player.pos]}. It has been {((curr_frame-last_frame)/1e9):2f}s since last f.")
                    last_frame = curr_frame

                    sleep(1/CameraConstants.RENDER_FRAMERATE)

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
                    if self.is_crashed:
                        Logger.log(f"[Physics Thread] Physics paused due to is_crashed being true. player@{[f'{num:2f}' for num in self.player.pos]}.")
                        sleep(0.01) # TODO - replace with continue or alternatively sleep until crash period ends
                        # continuing here is a bad idea, because we need to sleep to prevent the thread from running too fast
                        # and slowing everything down.
                    
                    # check collisions
                    self.player.curr_collisions = self.collision_handler.generate_collisions()
                    
                    # apply collision effects
                    for collision in self.player.curr_collisions:                    
                        # don't auto-run effect here if it requires click. That's a job for the key input thread.
                        
                        # run effect if it doesn't require click, unless it's already been activated and not multi_activate
                        if not collision.obj.data.get("requires_click") and not(collision.obj.has_been_activated and not collision.obj.data.get("multi_activate")):
                            self.collision_handler.run_collision_effect(collision)
                            collision.obj.has_been_activated = True
                            self.activated_objects.append(collision.obj)
                    
                    # after collisions is updated, tick physics.                
                    curr_time = time_ns()
                    self.player.tick((curr_time - self.last_tick)/1e9)
                    
                    _tps_str = f"{1e9/((curr_time-self.last_tick)):.2f}" if (curr_time-self.last_tick != 0) else "inf"
                    Logger.log(f"[Physics Thread] Player ticked. pos={self.player.pos[0]:.2f},{self.player.pos[1]:.2f}, yvel={self.player.yvel:.2f}, TPS: {_tps_str}")
                    self.last_tick = curr_time
                    
                    # DO NOT REMOVE. removing this slows down the renderer by A LOT
                    # even if the physics fps is like 389429 it still speeds things up a lot
                    # to have this sleep here. DONT ASK ME WHY IDK EITHER
                    sleep(1/EngineConstants.PHYSICS_FRAMERATE)
            except Exception as e:
                Logger.log(f"[Physics Thread] ERROR: {traceback.format_exc()}")
                self.running = False
        
        self.last_tick = time_ns()
        Thread(target=render_thread).start()
        Thread(target=physics_thread).start()
        
        # Main thread handles key input
        def _handle_keydown(event: KeyEvent) -> None:
            if str(event) in EngineConstants.QUIT_KEYS:
                self.running = False
                KeyboardListener.stop()
                return
            elif str(event) in EngineConstants.PAUSE_KEYS:
                self.pause()
                return
            # place a checkpoint if a user attempts to
            elif str(event) in EngineConstants.CHECKPOINT_KEYS and self.practice_mode:
                self.practicemodeobj.add_checkpoint(self.player.pos)
            # remove the most recent checkpoint if a user attempts to
            elif str(event) in EngineConstants.REMOVE_CHECKPOINT_KEYS and self.practice_mode:
                self.practicemodeobj.remove_checkpoint()
            elif str(event) in EngineConstants.JUMP_KEYS:
                
                something_got_activated = False
                
                # also go through the player's current collisions and
                # activate the first requires_click effect where "has_been_activated" is False
                for collision in self.player.curr_collisions:
                    if collision.obj.data.get("requires_click"):
                        
                        if collision.obj.data.get("multi_activate"): # always run effect if multi_activate
                            self.collision_handler.run_collision_effect(collision)
                            something_got_activated = True
                            break # can only perform one action per jump
                        
                        if not collision.has_been_activated: # run effect if not multi_activate and not activated
                            self.collision_handler.run_collision_effect(collision)
                            something_got_activated = True
                            collision.has_been_activated = True
                            self.activated_objects.append(collision.obj)
                            break # can only perform one action per jump
                
                # if nothing got activated, then jump
                if not something_got_activated:
                    self.player.request_jump()

        KeyboardListener.on_press = _handle_keydown
        KeyboardListener.start()

    def crash_normal(self, reseting: bool = False, restart: bool = True):
        """
        The old function for crash handling. Might convert to normal mode crash later on.
        """
        Logger.log(f"[Game/crash_normal]: Player crashed!")
        self.is_crashed = True
        #self.running=True
        # self.player=Player()
        #self.start_level()
        #self.running = False
        if not restart:
            self.running = False
            return

        sleep(EngineConstants.COOLDOWN_BETWEEN_ATTEMPTS)
        self.is_crashed = False
        self.player.reset_physics()
        for obj in self.activated_objects:
            obj.has_been_activated = False
        self.last_tick = time_ns() # this is to prevent moving forward while we are dead lol

        # if the player dies too quickly and is in practice mode, remove the most recent checkpoint
        if time.time() - self.game_start_time < 1 and self.practice_mode:
            self.practicemodeobj.remove_checkpoint()

        # reset game start time and last checkpoint time
        self.practicemodeobj.reset_checkpoint_time()
        self.game_start_time = time.time()

        # if player is in practice mode and there is a checkpoint, respawn the player at the checkpoint
        if self.practice_mode and self.practicemodeobj.is_checkpoint():
            # Logger.log(f"Last checkpoint is {self.practicemodeobj.last_checkpoint} so {self.practicemodeobj.is_checkpoint()}")
            x, y = self.practicemodeobj.get_last_checkpoint()
            self.player.pos = [x, y]

        # otherwise, restart the level by setting pos back to beginning 
        # also, NOTE: reset song if that is implemented
        self.attempt_number += 1

        # if reseting, restart the level
        if reseting:
            self.start_level()

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
        progresspercent = round((self.player.pos[0] / self.level.length) * 100)
        # sets selected index to play button
        pausemenuselectindex = 1
        Logger.log("drawing pause menu")

        # Draw pause menu background, progress bar, and buttons
        draw('assets/pausemenubg.png', Position.Relative(top=5, left=10), (self.camera.term.width - 20, self.camera.term.height * 2 - 20), 'scale')
        draw_text(f"Progress: {progresspercent}%", (self.camera.term.width) // 2 - 8, 10, bg_color='black')
        self.draw_pause_menu_buttons(pausemenuselectindex)

        Logger.log("pause menu drawn")

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
                            if not self.practice_mode:
                                self.practicemodeobj.clear_checkpoints()
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
        draw_text("Add Checkpoint - Z", ((self.camera.term.width) // 5) * 3 - 6, (self.camera.term.height + 20) // 2, bg_color='black')
        draw_text("Remove Checkpoint - X", ((self.camera.term.width) // 5) * 3 - 7, (self.camera.term.height + 25) // 2, bg_color='black')

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
        self.practicemodeobj.clear_checkpoints()
        self.crash_normal(True)

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
