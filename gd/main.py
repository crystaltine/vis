from render.camera import Camera
from render.utils import cls
from engine.objects import OBJECTS
from logger import Logger
from game import Game
from temp_parser import parse_level
from time import sleep

def main():

    leveldata = parse_level("test2.level")
    
    for row in leveldata:
        Logger.log(f"Level row types: {[type(row_obj) for row_obj in row]}")

    game = Game(leveldata)
    
    game.start_level()

if __name__ == "__main__":
    main()
    Logger.write()
    print("\x1b[0m")
    cls()
    sleep(0.1)
    print("Info: Exited game")