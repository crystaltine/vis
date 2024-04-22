from engine.objects import OBJECTS
from typing import List
from enum import Enum

class OBJECTS(Enum):
    block = 0
    spike = 1
    yellow_orb = 2
    purple_orb = 3
    blue_orb = 4

TEXT_TO_OBJECT = {
    " ": None,
    "x": OBJECTS.block,
    "^": OBJECTS.spike,
    "y": OBJECTS.yellow_orb,
    "p": OBJECTS.purple_orb,
    "b": OBJECTS.blue_orb,
}

OBJECT_TO_TEXT = {
    None: " ",
    OBJECTS.block: "x",
    OBJECTS.spike: "^",
    OBJECTS.yellow_orb: "y",
    OBJECTS.purple_orb: "p",
    OBJECTS.blue_orb: "b",
}

def write_to_file(objects: List[List[OBJECTS]], file_path: str):
    """
    Write a 2D array of game objects to a level file.

    Args:
        objects (List[List[OBJECTS]]): The 2D array of game objects to be written to the file.
        file_path (str): The path of the file to write the game objects to.

    Returns:
        None
    """
    with open(file_path, 'w') as file:
        for row in objects:
            line = ''
            for obj in row:
                line += ''.join(OBJECT_TO_TEXT[obj])
            file.write(line + '\n')

def read_from_file(file_path: str) -> List[List[OBJECTS]]:
    """
    Read from a level file and return the corresponding 2D array of game objects.

    Args:
        file_path (str): The path of the file that we will read the objects from.

    Returns:
        List[List[OBJECTS]]: The 2D array of game objects read from the file.
    """
    objects = []
    with open(file_path, 'r') as file:
        for line in file:
            row = []
            for char in line:
                if char == '\n':
                    continue
                row.append(TEXT_TO_OBJECT[char])
            objects.append(row)
        return objects


# Test the write_to_file and read_from_file functions
objects_array = [
    [OBJECTS.blue_orb, None],
    [None, OBJECTS.spike]
]

write_to_file(objects_array, 'gd/output.txt')  
objects_array = read_from_file('gd/output.txt')

for row in objects_array:
    for item in row:
        print(item, end=' ')
    print()