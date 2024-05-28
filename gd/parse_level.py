
from engine.objects import OBJECTS, LevelObject
from typing import List
from logger import Logger

SUPPORTED_CHARS = {
    " ": None,
    "0": OBJECTS.block0_0,
    "1": OBJECTS.block0_1,
    "2": OBJECTS.block0_2,
    "3": OBJECTS.block0_3,
    "^": OBJECTS.spike,
    "y": OBJECTS.yellow_orb,
    "p": OBJECTS.purple_orb,
    "b": OBJECTS.blue_orb,
}

def parse_level(filename: str) -> List[List[LevelObject]]:
    """
    Parses a file that contains leveldata. The file
    must be located in the levels/ folder.
    
    The file should only be spaces and keys in the SUPPORTED_CHARS dict.
    [0,1,2,3]'s are blocks, ^'s are spikes, spaces are blank, y's are yellow orbs, p's are purple orbs, etc.
    Refer to the SUPPORTED_CHARS dict for any more.
    
    The grid matches how it works in game.
    This means each row is a row of objects.
    the last line of the file is the ground row. (just above the ground)
    
    Returns a list of `None`s and objects.
    
    # Example level:
    ```
               p     y^^^
              ^^^    xxxx
    ```    
    """
    
    with open(f"levels/{filename}", "r") as f:
        lines = f.readlines()
        
        leveldata: List[List[LevelObject]] = []
        
        for reversed_y in range(len(lines)):
            row = []
            for x in range(len(lines[reversed_y])):
                if lines[reversed_y][x] in SUPPORTED_CHARS:
                    row.append(LevelObject(SUPPORTED_CHARS[lines[reversed_y][x]], x, len(lines)-reversed_y-1))
                    #Logger.log(f"just added an object, t.data's type is: {type(t.data)}")
            leveldata.append(row)
        
        f.close()
                
    # make sure every row is the same length.
    longest_row = max(len(row) for row in leveldata)
    
    for i in range(len(leveldata)):
        
        # add None objects to end of every row to make them the same length
        while len(leveldata[i]) < longest_row:
            leveldata[i].append(LevelObject(None, len(leveldata[i]), len(leveldata)-i))
    
    return leveldata

def test_parse_level(filename): 

    for i in range(0, len(parse_level(filename)), 1): 
        for j in range(0, len(parse_level(filename)[i]), 1):

            if parse_level(filename)[i][j].data is None: 
                print("None")
                print('\n')
            else: 
                print(parse_level(filename)[i][j].data["name"])
                print('\n')
#test_parse_level("test2.level")
#test_parse_level("test.level")
