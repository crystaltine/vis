from typing import List
import blessed
import game

class transform:
    gameTerm = blessed.Terminal()
    def ArrayToLevel (self, level:List[List[game.LevelObject]]):
        for obj in level: 
            self.gameTerm(obj)