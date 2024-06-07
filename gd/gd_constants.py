from blessed import Terminal
from typing import List, Tuple, Dict
from enum import Enum

class GDConstants:
    """ General constants for the game and stuff """
    
    term = Terminal()
    
    NUM_BLOCK_TEXTURES = 13
    NUM_SPIKE_TALL_TEXTURES = 3
    NUM_SPIKE_SHORT_TEXTURES = 5
    NUM_SPIKE_FLAT_TEXTURES = 2
    
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