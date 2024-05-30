from blessed import Terminal
from typing import List, Tuple, Dict
from enum import Enum

class GD:
    """
    General class for broad game elements.
    Currently used for holding THE terminal instance, accessible from all parts of the game.
    """
    
    term = Terminal()
    
class GDConstants:
    """ General constants for the game and stuff """
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
        robot = "robot"
        spider = "spider"
        swing = "swing"
        
    class speeds(Enum):
        half = "half"
        normal = "normal"
        double = "double"
        triple = "triple"
        quadruple = "quadruple"
        
    class gravities(Enum):
        normal = "normal"
        reverse = "reverse"