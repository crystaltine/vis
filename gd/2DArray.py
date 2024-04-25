from typing import List
import blessed
import game

class transform:
    #terminal
    gameTerm = blessed.Terminal()
    def ArrayToLevel (self, level:List[List['game.LevelObject']]) :
        """
        Uses a 2D array of Level Objects and creates the level based on the x and y position of each object 

        level: the 2D array of LevelObjects 
        """
        for obj in level: 
            obj:game.LevelObject
            term_xpos = obj.x
            term_ypos = obj.y
            self.gameTerm.move_xy(term_xpos, term_ypos)
            print(obj.data.get("ASCII"))