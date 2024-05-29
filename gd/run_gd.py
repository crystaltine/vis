from render.camera import Camera
from render.utils import cls
from engine.objects import OBJECTS
from logger import Logger
from game import Game
from parse_level import parse_level
from time import sleep

def run_level(path: str):
    """
    `path: str` - the path to the level file to be run. (e.g. "levels/level1.txt")
    """
    leveldata = path
    if isinstance(leveldata,str):
        leveldata = parse_level(leveldata)

    game = Game(leveldata)
    game.start_level()