from render.camera import Camera
from engine.objects import OBJECTS
from game import Game
from time import sleep
from logger import Logger

def main():
    leveldata = [
        [None, None, None, OBJECTS.spike, OBJECTS.spike, None, None         ],
        [None, None, None, OBJECTS.block, OBJECTS.block, None, OBJECTS.spike],
        [None, None, None, None,          None,          None, OBJECTS.block],
    ]

    game = Game(leveldata)

    game.start_level()

if __name__ == "__main__":
    main()
    Logger.write()