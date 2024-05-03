from typing import List
import blessed
import game

class transform:
    
    gameTerm = blessed.Terminal()

    def Temp2DArrayToTerm (self, level:List[List['game.LevelObject']], key="temp_symbol") :
        """
        Uses a 2D array of Level Objects and creates the level based on the x and y position of each object 

        level: the 2D array of LevelObjects 

        key: used to identify the data wanted for each object in the 2D Array 
        """
        for row in level: 
            for obj in row: 
                "Type Hinted obj to LevelObject to obtain access to its data"
                obj:game.LevelObject
                "Object position in the level"
                term_xpos = obj.x
                term_ypos = obj.y
                self.gameTerm.move_xy(term_xpos, term_ypos)
                print(obj.data.get(key))
