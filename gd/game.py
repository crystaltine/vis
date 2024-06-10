from typing import Tuple, Literal
import json
from time import time_ns, sleep
from threading import Thread
import traceback
import time

from logger import Logger
from render.camera import Camera
from render.constants import CameraConstants
from engine.constants import EngineConstants
from engine.player import Player
from engine.collision_handler import CollisionHandler
from draw_utils import Position, draw_rect
from img2term.main import draw
from bottom_menu import draw_text
from level import Level
from keyboard.keyboard_listener import KeyboardListener
from keyboard.key_event import KeyEvent
from practice_mode import PracticeMode
from gd_constants import GDConstants
from audio import AudioHandler
from render.texture_manager import TextureManager
from menus.official_levels_menu import OfficialLevelsMenu

class Game:
    """
    Represents a level "world" and contains a player object.

    Coordinates keyboard, render, physics threads, etc.
    """

    def __init__(self, level: Level):
        self.level = level

        self.camera = Camera(self.level)
        self.collision_handler = CollisionHandler(self)
        self.audio_handler = AudioHandler(level.metadata.get("song_filepath"), level.metadata.get("song_start_time"))
        self.player = Player(self)

        self.is_crashed = False
        """ Special flag for when the player has crashed. (kinda like a pause)"""
        
        self.running = False
        """ Pause-switch. Render & physics threads pause if this is False. """
        
        self.exiting = False
        """ kill-switch for all game threads. """
        
        self.need_to_render_raw = False
        """ Set to True upon unpausing, so that the next frame completely removes the pause menu. """
        
        self.last_tick = None
        
        self.activated_objects = []
        """ Stores which objects had their activated properties set to true, so we can reset them on crash. """        

        self.pausemenuselectindex = 1
        self.changed = False
        self.practice_mode = False
        # creating object that will handle practice mode functionality
        self.practicemodeobj = PracticeMode(self)
        self.last_checkpoint = None
        self.checkpoints = []
        self.attempt_number = 1
        self.game_start_time = time.time()
        
        self.highest_percent_this_session = 0
        """ Stores the highest percentage achieved in this session. Resets upon changing between practice/normal mode. """

    def _main_keydown_handler(self, event: KeyEvent) -> None:
        if str(event) in GDConstants.KILL_KEYS:
            self.exiting = True
            KeyboardListener.stop()
            return
        elif str(event) in GDConstants.PAUSE_KEYS and not self.is_crashed:
            self.pause()
            return
        # place a checkpoint if a user attempts to
        elif str(event) in GDConstants.CHECKPOINT_KEYS and self.practice_mode:
            self.practicemodeobj.add_checkpoint(self.player.pos)
        # remove the most recent checkpoint if a user attempts to
        elif str(event) in GDConstants.REMOVE_CHECKPOINT_KEYS and self.practice_mode:
            self.practicemodeobj.remove_checkpoint()
        elif str(event) in GDConstants.JUMP_KEYS:
            
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
                    
            if self.player.gamemode == 'wave':
                # add to wave trail pivots if in wave gamemode
                self.player._create_wave_pivot()
            
            # if nothing got activated, then jump
            if not something_got_activated:
                self.player.request_jump()
    
    def _main_keyup_handler(self, event: KeyEvent) -> None:
        if str(event) in GDConstants.JUMP_KEYS:
            if self.player.gamemode == 'wave':
                self.player._create_wave_pivot()

    def start_level(self) -> None:
        """
        Begin a separate thread to run level physics/animation ticks
        """

        self.running = True
        
        self.camera.render_init()
        def render_thread():
            try:
                last_frame = time_ns()
                while True:
                    
                    if self.exiting:
                        break 
                    
                    if not self.running:
                        sleep(0.01)
                        continue
                    
                    curr_frame = time_ns()
                    
                    fps_str = f"{(1e9/(curr_frame-last_frame)):2f}" if (curr_frame-last_frame != 0) else "inf"
                    #if self.is_crashed:
                    #    Logger.log(f"[Game/render_thread] Rendering CRASHED frame, player@{[f'{num:2f}' for num in self.player.pos]}. FPS: {fps_str}")
                    #else:
                    #    Logger.log(f"[Game/render_thread] Rendering LIVE frame, player@{[f'{num:2f}' for num in self.player.pos]}. FPS: {fps_str}")
                    
                    # adds a checkpoint if its been over 2 seconds since the last checkpoint was added
                    if self.practice_mode and self.practicemodeobj.is_checkpoint_time_over():
                        self.practicemodeobj.add_checkpoint(self.player.pos)

                    if self.need_to_render_raw:
                        self.camera.render(self, render_raw=True)
                        self.need_to_render_raw = False
                    else:
                        self.camera.render(self)
                    
                    # renders the most recent checkpoint if it exists
                    # note: this has been moved to Camera.render
                    # if self.last_checkpoint:
                    #     self.camera.draw_checkpoint(self.player.pos[0], self.last_checkpoint[0], self.last_checkpoint[1])
                    
                    #Logger.log(f"Just rendered frame with player@{[f'{num:2f}' for num in self.player.pos]}. It has been {((curr_frame-last_frame)/1e9):2f}s since last f.")
                    last_frame = curr_frame

                    sleep(1/CameraConstants.RENDER_FRAMERATE)
            except:
                Logger.log(f"[Render Thread] ERROR: {traceback.format_exc()}")
                self.exiting = True    

        def check_if_level_complete():
            if self.player.pos[0]-EngineConstants.END_OF_LEVEL_PADDING>=self.level.length:

                self.running = False
                
                new_frame=self.camera.curr_frame.copy()
                new_frame.add_rect((0,0,0), 0, 0, new_frame.width, new_frame.height)
                new_frame.add_text(int(new_frame.width*0.5), int(new_frame.height*0.1), TextureManager.font_title, 'Level Complete')
                new_frame.add_text(int(new_frame.width*0.5), int(new_frame.height*0.5), TextureManager.font_small1, f"Total Attempts: {self.attempt_number}")
                new_frame.render(self.camera.curr_frame)

                self.highest_percent_this_session = 100
                self.write_highest_progress_to_file()

        def physics_thread():
            while True:
                try:
                    #Logger.log(f"running physics tick. player pos is {self.player.pos[0]:.2f},{self.player.pos[1]:.2f}, time_ns is {time_ns()}")
                    if self.exiting:
                        self.audio_handler.stop_playing_song()
                        self.write_highest_progress_to_file() # IMPORTANT - must do this before stopping listener,
                        # otherwise menuhandler wont render the new progress since it starts rendering the next
                        # menu right as soon as keyboard listener stops.
                        KeyboardListener.stop()
                        break
                    
                    if self.is_crashed or not self.running:
                        #Logger.log(f"[Physics Thread] Physics paused due to is_crashed being true. player@{[f'{num:2f}' for num in self.player.pos]}.")
                        sleep(0.01) # TODO - replace with continue or alternatively sleep until crash period ends
                        continue
                        # continuing here is a bad idea, because we need to sleep to prevent the thread from running too fast
                        # and slowing everything down.
                    #try:
                    self.highest_percent_this_session = max(self.highest_percent_this_session, self.get_progress_percentage())
                    #except:
                    #    Logger.log(f"[Physics Thread] ERROR: {traceback.format_exc()}")
                    # check if the level is complete
                    check_if_level_complete()
                    
                    self.level.check_color_triggers(self.player.pos[0])

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
                    #Logger.log(f"[Physics Thread] Player ticked. pos={self.player.pos[0]:.2f},{self.player.pos[1]:.2f}, yvel={self.player.yvel:.2f}, TPS: {_tps_str}")
                    self.last_tick = curr_time
                    
                    # DO NOT REMOVE. removing this slows down the renderer by A LOT
                    # even if the physics fps is like 389429 it still speeds things up a lot
                    # to have this sleep here. DONT ASK ME WHY IDK EITHER
                    sleep(1/EngineConstants.PHYSICS_FRAMERATE)
                except Exception as e:
                    Logger.log(f"[Physics Thread] ERROR: {traceback.format_exc()}")
                    self.exiting = True
                    break
        
        self.last_tick = time_ns()
        Thread(target=render_thread).start()
        Thread(target=physics_thread).start()
        self.audio_handler.begin_playing_song()

        KeyboardListener.add_on_press(self._main_keydown_handler)
        KeyboardListener.add_on_release(self._main_keyup_handler)
        KeyboardListener.start()
        
        KeyboardListener.listener.join()

    def crash(self):
        """ Run when a player DIES (not when they click restart button) """
        
        Logger.log(f"[Game/crash_normal]: Player crashed! (died, not restarted)")
        
        self.audio_handler.stop_song_and_play_crash()
        self.is_crashed = True

        sleep(EngineConstants.COOLDOWN_BETWEEN_ATTEMPTS)

        # if the player dies too quickly and is in practice mode, remove the most recent checkpoint
        if time.time() - self.game_start_time < 2 and self.practice_mode:
            self.practicemodeobj.remove_checkpoint()

        # reset game start time and last checkpoint time
        self.practicemodeobj.reset_checkpoint_time()
        self.game_start_time = time.time()
        
        # if player is in practice mode and there is a checkpoint, respawn the player at the checkpoint
        if self.practice_mode and self.practicemodeobj.is_checkpoint():

            self.reset_level(self.practicemodeobj.get_last_checkpoint())
        else: # restart at beginning of level
            self.reset_level()
        
    def reset_level(self, new_pos: Tuple[int, int] = None) -> None:
        """ 
        Runs logic for resetting the level, but doesnt do anything about crash logic (playing sound, etc.) 
        
        Here's what this func does:
        - Stops the song if its playing
        - Sets self.is_crashed to False
        - Resets the player's physics
        - Resets the activated objects (sets their has_been_activated to False)
        - Resets the last tick time to now (prevent moving forward while not alive)
        - adds 1 to the attempt number
        - begins playing the song again
        """
        
        self.audio_handler.stop_playing_song()
        self.is_crashed = False
        
        self.player.reset_physics(new_pos)
        for obj in self.activated_objects:
            obj.has_been_activated = False
        self.last_tick = time_ns() # this is to prevent moving forward while we are dead lol

        # reset the player's position if a new position is given
        if new_pos:
            x, y = new_pos
            self.player.pos = [x, y] 
            
        new_y = self.player.ORIGINAL_START_POS[1]
        if new_pos is not None:
            new_y = new_pos[1]

        # reset camera bottom back to ground
        self.camera.camera_bottom = -CameraConstants.GROUND_HEIGHT
        self.camera.player_y_info = {
            "physics_pos": new_y,
            "screen_pos": self.camera.px_height - CameraConstants.GROUND_HEIGHT*CameraConstants.BLOCK_HEIGHT - CameraConstants.BLOCK_HEIGHT
        }

        self.level.reset_colors()
        self.level.reset_color_trigger_cache()

        # reset the game start time
        self.game_start_time = time.time()

        self.attempt_number += 1
        
        # start song again
        self.audio_handler.begin_playing_song()
        
    def get_progress_percentage(self) -> int:
        #return 1# test

        # calculates progress bar based on length of level and player position
        dist_from_start = self.player.pos[0]-self.level.metadata["start_settings"]["position"][0]
        true_level_len = self.level.length+EngineConstants.END_OF_LEVEL_PADDING-self.level.metadata["start_settings"]["position"][0]
        progresspercent = round(min(100, (dist_from_start/true_level_len)*100))
                    
        return progresspercent
    
    def write_highest_progress_to_file(self, mode_override: Literal["practice", "normal"] = None) -> None:
        """ Writes the highest progress percentage achieved in this session to the level file.
        changes which mode based on self.practice_mode = True or not.
        
        Can override which mode to save to by passing in mode_override.
        """
        
        f = open(self.level.filepath)
        data = json.load(f)
        
        key = 'progress_practice' if (self.practice_mode or mode_override == "practice") else 'progress_normal'
        if mode_override is not None:
            key = f"progress_{mode_override}"
            
        Logger.log(f"writing highest progress to {key}, progress is {self.highest_percent_this_session}")
        
        if data['metadata'][key]<self.highest_percent_this_session:
            data['metadata'][key]=self.highest_percent_this_session/100
            json.dump(data,open(self.level.filepath, 'w'))
            
        # update the level menu
        OfficialLevelsMenu.update_level_progress(self.level.filepath, self.highest_percent_this_session/100, key)
        

    def pause(self) -> None:
        """
        Pauses the game and displays the pause menu.
        Draws the pause menu background, progress bar, and pause menu buttons. 
        Then passes off handling user interaction with the pause menu.
        Also sets initial selected index to the play button.
        """
        
        #Logger.log(f"pause")
        # stops the game and sets paused to true
        self.running = False
        # calculates progress bar based on length of level and player position
        progresspercent = self.get_progress_percentage()
        # sets selected index to play button
        self.pausemenuselectindex = 1
        
        self.audio_handler.pause_playing_song()
        
        # temporarily remove physics key handlers
        # and replace them with the pause menu key handler
        KeyboardListener.remove_on_press(self._main_keydown_handler)
        KeyboardListener.remove_on_release(self._main_keyup_handler)
        KeyboardListener.add_on_press(self._pause_menu_keydown_handler)
        
        #Logger.log(f"pause(): handlers changed!!, press/rel now has size {len(KeyboardListener.on_presses)}/{len(KeyboardListener.on_releases)}")
        
        # Draw pause menu background, progress bar, and buttons
        draw('assets/pausemenubg.png', Position.Relative(top=5, left=10), (GDConstants.term.width - 20, GDConstants.term.height * 2 - 20), 'scale')
        draw_text(f"Progress: {progresspercent}%", (GDConstants.term.width) // 2 - 8, 10, bg_color='black')
        self.draw_pause_menu_buttons()
        
        Logger.log(f"reached end of pause func")

    def _pause_menu_keydown_handler(self, event: KeyEvent) -> None:
        if str(event) == 'left':
            self.pausemenuselectindex = (self.pausemenuselectindex - 1) % 4
            self.changed = True
            
        elif str(event) == 'right':
            self.pausemenuselectindex = (self.pausemenuselectindex + 1) % 4
            self.changed = True
        
        elif str(event) in GDConstants.PAUSE_KEYS and self.running == False:
            #Logger.log(f"unpausing cuz pause_keys")
            self.unpause()
            return
        
        elif str(event) == 'enter':
            if self.pausemenuselectindex == 0:
                self.restart()
            elif self.pausemenuselectindex == 1:
                #Logger.log(f"unpausing cuz hit button")
                self.unpause()
                return
            elif self.pausemenuselectindex == 2:
                self.practice_mode = not self.practice_mode
                if not self.practice_mode: # if changing back to normal mode
                    
                    # save the highest percent achieved in this session to practice, then reset to 0
                    self.write_highest_progress_to_file("practice")
                    self.highest_percent_this_session = 0
                    
                    self.practicemodeobj.clear_checkpoints()
                else:
                    # save highest progress to normal, then dont reset
                    self.write_highest_progress_to_file("normal")
                self.restart() # restart the level if changing to normal mode
                
            elif self.pausemenuselectindex == 3:
                self.exiting = True
                KeyboardListener.remove_on_press(self._pause_menu_keydown_handler)
                
        if self.changed and not self.exiting:
            self.draw_pause_menu_buttons()
            self.changed = False 

    def draw_pause_menu_buttons(self) -> None:
        """
        Draws the pause menu buttons with highlights based on the selected index.
        Args:
            index (int): The index of the currently selected menu button.
        """

        #Logger.log(f"drawing pause menu buttons with index {self.pausemenuselectindex}")

        # OLD TEXT BASED RENDERING OF BUTTONS
        # draw_text("Reset", 10 + ((GDConstants.term.width - 50) // 4), (GDConstants.term.height) // 2, bg_color='white' if index == 0 else 'black')
        # draw_text("Play", 10 + ((GDConstants.term.width - 50) // 4) * 2, (GDConstants.term.height) // 2, bg_color='white' if index == 1 else 'black')
        # draw_text("Practice", 10 + ((GDConstants.term.width - 50) // 4) * 3, (GDConstants.term.height) // 2, bg_color=practice_bg_color)
        # draw_text("Exit", 10 + ((GDConstants.term.width - 50) // 4) * 4, (GDConstants.term.height) // 2, bg_color='white' if index == 3 else 'black')


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
            selected = '_selected' if self.pausemenuselectindex == i else ''
            suffix = practice_bg_color if label == "practice_button" and not selected else selected
            draw(f"assets/pause_menu/{label}{suffix}.png", pos=Position.Relative(left=positions[i], bottom="calc(55% - 10ch)"))

        # Draw additional text labels for controls
        draw_text("Add Checkpoint - Z", ((GDConstants.term.width) // 5) * 3 - 6, (GDConstants.term.height + 20) // 2, bg_color='black')
        draw_text("Remove Checkpoint - X", ((GDConstants.term.width) // 5) * 3 - 7, (GDConstants.term.height + 25) // 2, bg_color='black')

    def unpause(self) -> None:
        """ Unpauses the level. """
        self.running = True
        self.need_to_render_raw = True
        self.last_tick = time_ns()
        
        # exchange key handlers again
        KeyboardListener.add_on_press(self._main_keydown_handler)
        KeyboardListener.add_on_release(self._main_keyup_handler)
        KeyboardListener.remove_on_press(self._pause_menu_keydown_handler)
        
        #Logger.log(f"UNpause(): handlers changed!, press/release now has size {len(KeyboardListener.on_presses)}/{len(KeyboardListener.on_releases)}")
        
        self.audio_handler.resume_playing_song()
        #self.start_level()

    def restart(self) -> None:
        """
        Run when the player clicks the restart button. (similar to crash except they didnt die)
        """

        # in pract mode, dont clear checkpoints
        #self.practicemodeobj.clear_checkpoints()
        self.unpause()
        self.reset_level()
        
        #self.start_level()

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
