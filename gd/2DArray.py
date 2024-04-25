from typing import List
import blessed
import game

class transform:
    gameTerm = blessed.Terminal()
    def ArrayToLevel (self, level:List[List[game.LevelObject]], key):
        for obj in level: 
            obj:game.LevelObject
            term_xpos = obj.x
            term_ypos = obj.y
            self.gameTerm.move_xy(term_xpos, term_ypos)
            self.gameTerm(obj.__getitem__(key))