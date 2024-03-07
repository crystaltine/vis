from engine.objects import OBJECTS
from logger import Logger

SUPPORTED_CHARS = {
    " ": None,
    "x": OBJECTS.block,
    "^": OBJECTS.spike,
    "y": OBJECTS.yellow_orb,
    "p": OBJECTS.purple_orb,
    "b": OBJECTS.blue_orb,
}

def parse_level(filename: str) -> list:
    """
    Parses a file that contains leveldata. The file
    must be located in the levels/ folder.
    
    The file should only be spaces and keys in the SUPPORTED_CHARS dict.
    x's are blocks, ^'s are spikes, spaces are blank, y's are yellow orbs, p's are purple orbs.
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
        
        leveldata = []
        
        for line in lines:
            row = []
            for char in line:
                if char in SUPPORTED_CHARS:
                    row.append(SUPPORTED_CHARS[char])
            leveldata.append(row)
        
        f.close()
                
    # make sure every row is the same length.
    longest_row = max(len(row) for row in leveldata)
    
    for row in leveldata:
        row.extend([None]*(longest_row-len(row)))
        
    # IMPORTANT: add 10 Nones to beginning of every level. This is to offset the player render
    # without having to deal with negative grid values.
    
    for row in leveldata: row[:0] = [None]*10
    
    return leveldata
    