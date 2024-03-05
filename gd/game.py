from engine.objects import OBJECTS
from engine.constants import CONSTANTS
from engine.player import Player
from render.camera import Camera
from time import time_ns, sleep
from threading import Thread
from math import floor, ceil

class Game:
    """
    Represents a level "world" and contains a player object.

    Handles physics ticks for the player and animations
    """

    def __init__(self, leveldata=None):
        """
        Creates a `Player` object automatically.
        """

        self.leveldata = leveldata or [
            [],
            [],
            [],
            [],
            [OBJECTS.block, OBJECTS.block],
            [OBJECTS.spike],
            [OBJECTS.spike],
            [OBJECTS.spike],
        ]
        """
        Each column's objects start at the bottom (on the ground)
        """

        self.player = Player()
        self.camera = Camera(self.leveldata)

        self.running = False
        self.last_tick = None

    def start_level(self):
        """
        Begin a separate thread to run level physics/animation ticks
        """

        self.running = True

        # Initialize camera rendering
        self.camera.render_init()

        def render_thread():
            while True:
                self.camera.render(self.player.pos[0])
                sleep(1/CONSTANTS.TARGET_FRAMERATE)

                if not self.running:
                    break

        def physics_thread():
            while True:
                self.player.tick((time_ns() - self.last_tick)/1e9)

                if not self.running:
                    break

                """
                # check collisions
                colliding_obj = self.check_collisions()

                # apply effects
                for obj in colliding_obj:
                    effect = obj.get("collide_effect")
                    if effect is not None:
                        stop = self.run_effect(effect)

                        if stop: 
                            self.running = False
                            break
                             # e.g. if crash, then no need to keep looping

                if not self.running:
                    break
                """
        
        self.last_tick = time_ns()
        Thread(target=render_thread).start()
        Thread(target=physics_thread).start()

    def run_effect(self, effect):
        if effect == 'neg-gravity':
            self.player.gravity = -CONSTANTS.GRAVITY
        elif effect == 'pos-gravity':
            self.player.gravity = CONSTANTS.GRAVITY
        elif effect == 'crash':
            self.crash()
        else:
            return # unknown, do nothing

    def crash(self):
        self.running = False
        sleep(1)
        exit() # TODO

    def check_collisions(self) -> list:
        """
        Returns a list of objects that the player is currently touching.
        """

        # TODO - for now, we only search in the one or two columns the player is in,
        # since we dont have any large hitboxes yet.

        touching = []

        # check the blocks within 3 blocks of the player's y-value
        y_check_range = [floor(self.player.pos[1] - 3), ceil(self.player.pos[1] + 3)]
        
        for x in [
        floor(self.player.pos[0]-CONSTANTS.PLAYER_HITBOX_X/2), 
        ceil(self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X/2)]:

            for y in [
            max(0, y_check_range[0]), 
            min(len(self.leveldata[x]), y_check_range[1])]:

                # check collisions
                obj = self.leveldata[x][y]

                if obj["hitbox_type"] == "hostile":

                    # check x collision
                    if (
                    x+obj["hitbox_xrange"][0] < self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X/2 or
                    x+obj["hitbox_xrange"][1] > self.player.pos[0]-CONSTANTS.PLAYER_HITBOX_X/2):
                        touching.append(obj)

                    # check y collision
                    elif (
                    y+obj["hitbox_yrange"][0] > self.player.pos[1]-CONSTANTS.PLAYER_HITBOX_Y/2 or
                    y+obj["hitbox_yrange"][1] < self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y/2):
                        touching.append(obj)

                elif obj["hitbox_type"] == "solid":

                    # TODO - somehow figure out the walking on top part

                    # check x collision
                    if (
                    x+obj["hitbox_xrange"][0] < self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X/2 or
                    x+obj["hitbox_xrange"][1] > self.player.pos[0]-CONSTANTS.PLAYER_HITBOX_X/2):
                        touching.append(obj)

                    # check y collision ONLY FOR THE BOTTOM SIDE
                    elif (
                    y+obj["hitbox_yrange"][0] < self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y/2 or
                    y+obj["hitbox_yrange"][1]-CONSTANTS.SOLID_SURFACE_LENIENCY > self.player.pos[1]-CONSTANTS.PLAYER_HITBOX_Y/2):
                        touching.append(obj)

                elif obj["hitbox_type"] == "ghost":
                    
                    # check x collision
                    if (
                    x+obj["hitbox_xrange"][0] < self.player.pos[0]+CONSTANTS.PLAYER_HITBOX_X/2 or
                    x+obj["hitbox_xrange"][1] > self.player.pos[0]-CONSTANTS.PLAYER_HITBOX_X/2):
                        touching.append(obj)

                    # check y collision
                    elif (
                    y+obj["hitbox_yrange"][0] > self.player.pos[1]-CONSTANTS.PLAYER_HITBOX_Y/2 or
                    y+obj["hitbox_yrange"][1] < self.player.pos[1]+CONSTANTS.PLAYER_HITBOX_Y/2):
                        touching.append(obj)
