from blessed import Terminal
from typing import List, Tuple, Dict
from enum import Enum

class GDConstants:
    """ General constants for the game and stuff """
    
    term = Terminal()
    
    _VERSION = "b1.2"
    
    KILL_KEYS = ['\x03']
    QUIT_KEYS = ['q', '\x1b', 'esc', "KEY_ESCAPE"] # active on menus
    JUMP_KEYS = [' ', 'up', 'w', 'KEY_UP', "W"]
    PAUSE_KEYS = ['p', 'KEY_ESCAPE', 'esc'] # active in levels
    CHECKPOINT_KEYS = ['z']
    REMOVE_CHECKPOINT_KEYS = ['x']
    
    NUM_BLOCK_TEXTURES = 13
    NUM_SPIKE_TALL_TEXTURES = 3
    NUM_SPIKE_SHORT_TEXTURES = 5
    NUM_SPIKE_FLAT_TEXTURES = 2
    
    AUDIO_VOLUME = 0.5
    
    class difficulties(Enum):
        na = "na"
        auto = "auto"
        easy = "easy"
        normal = "normal"
        hard = "hard"
        harder = "harder"
        insane = "insane"
        demon = "demon"
        
    class gamemodes(Enum):
        cube = "cube"
        ship = "ship"
        ball = "ball"
        ufo = "ufo"
        wave = "wave"
        spider = "spider"
        
    supports_jumping = [gamemodes.cube.value, gamemodes.ball.value, gamemodes.ufo.value, gamemodes.spider.value]
        
    class speeds(Enum):
        half = "half"
        normal = "normal"
        double = "double"
        triple = "triple"
        quadruple = "quadruple"
        
    class gravities(Enum):
        normal = "normal"
        reverse = "reverse"