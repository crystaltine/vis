from render.camera import Camera
from render.utils import cls
from engine.objects import OBJECTS
from logger import Logger
from game import Game
from parser import parse_level
from time import sleep

def run_level(path: str):
    """
    `path: str` - the path to the level file to be run. (e.g. "levels/level1.txt")
    """
    leveldata = path
    if isinstance(leveldata,str):
        leveldata = parse_level(leveldata)
        for row in leveldata:
            Logger.log(f"Level row types: {[type(row_obj) for row_obj in row]}")

    game = Game(leveldata)
    
    game.start_level()