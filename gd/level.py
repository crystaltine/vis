from typing import List, Tuple, Dict, TYPE_CHECKING, Literal, TypedDict
from copy import deepcopy

from GD import GDConstants
from render.constants import CameraConstants

class StartSettings(TypedDict):
    bg_color: CameraConstants.RGBTuple
    ground_color: CameraConstants.RGBTuple
    position: Tuple[int, int] | None # defaults to (0, 0)
    gamemode: GDConstants.gamemodes
    speed: GDConstants.speeds
    gravity: GDConstants.gravities

class OfficialLevelMetadata(TypedDict):
    """ Metadata schema for official (built-in) levels """
    type: Literal["official"]
    start_settings: StartSettings
    name: str
    song_filepath: str
    song_start_time: float
    total_attempts: int
    progress_normal: int
    progress_practice: int
    
class CreatedLevelMetadata(TypedDict):
    """ Metadata schema for locally saved created levels """
    type: Literal["created"]
    start_settings: StartSettings
    name: str
    description: str
    song_filepath: str
    song_start_time: float
    created_timestamp: float
    modified_timestamp: float
    autosave: bool
    total_attempts: int
    progress_normal: int # 100% = verified
    progress_practice: int
    
class OnlineLevelMetadata(TypedDict):
    """ Metadata schema for online levels (downloaded/search results) """
    type: Literal["online"]
    start_settings: StartSettings
    id: str
    name: str
    description: str
    author: str
    song_filepath: str
    song_start_time: float
    created_timestamp: float
    modified_timestamp: float   
    downloads: int
    likes: int
    difficulty: GDConstants.difficulties
    total_attempts: int
    progress_normal: int
    progress_practice: int

LevelMetadata = OfficialLevelMetadata | CreatedLevelMetadata | OnlineLevelMetadata

class Level:
    """ Class that contains helpful methods related to levels.
    Holds a 2D List of LevelObjects | Nones, and also metadata about the level. 
    The 2D list should also be rectangular - all rows should be the same length.
    """

    def __init__(self, metadata: LevelMetadata, leveldata: List[List["LevelObject"]]):
        self.metadata = metadata
        self.leveldata: List[List["LevelObject"]] = leveldata
        """ The backend level data. SHOULD be rectangular - see level_parser """
        
        self.width = len(leveldata[0])
        """ The width of the level. Ends at the last object (rightmost object)"""
        self.height = len(leveldata)
        """ The height of the level. """
        
        self.color_channels: Dict[int, Tuple[int, int, int]] = {}
        """ Dict of id -> RGB color. Objects can reference these IDs to get their color. """
        
        self.bg_color = metadata["start_settings"]["bg_color"]
        self.ground_color = metadata["start_settings"]["ground_color"]
    
    # TODO: implement this
    def parse(self, level_filepath: str) -> "Level":
        """ Parses a level file (using the new JSON-based system) and returns a Level object."""
        pass
        
    def get_object_at(self, x: int, y: int) -> "LevelObject" | None:
        """
        Return a reference to the LevelObject at these specific coordinates.
        
        Remember that x=0,y=0 is the bottom left corner of a level, and that
        coordinates refer to the bottom left corner of a LevelObject.
        """
        
        row_index = len(self.leveldata) - y - 1
        return self.leveldata[row_index][x]
    
    def get_row(self, y: int) -> List["LevelObject"]:
        """ Return a list of LevelObjects at a specific y-coordinate. """
        return self.leveldata[len(self.leveldata) - y - 1]
    
    def set_color_channel(self, id: int, new_color: CameraConstants.RGBTuple):
        """ Update the color of a color channel. Creates a new channel if it doesn't exist. """
        self.color_channels[id] = new_color
        
    def get_color_channel(self, id: int) -> CameraConstants.RGBTuple:
        """ Get the color of a color channel. If the channel was never set, sets it to `(255, 255, 255)` (white) and returns that. """
        self.color_channels.setdefault(id, (255, 255, 255))
        return self.color_channels[id]
        
class LevelObject:
    """
    Represents a single object in a level. object types must be found in the `engine.objects.OBJECTS` dict.
    These should be created on level load, and NOT on every tick.
    
    Contains other data such as has_been_activated, position, (in the future, group, color, etc.)
    """
    def __init__(self, obj_dict: dict, posx: float, posy: float):
        self.data = deepcopy(obj_dict)
        
        self.type = obj_dict.get("name")
        """ The type of object this is. """
        
        self.x: float = posx
        """ Represents the left x-position of the object """
        self.y: float = posy
        """ Represents the bottom y-position of the object """
        
        self.rotation: CameraConstants.ROTATIONS = CameraConstants.ROTATIONS.UP
        """ Represents the rotation of the object. """
        self.reflection: CameraConstants.REFLECTIONS = CameraConstants.REFLECTIONS.NONE
        """ Represents the reflection of the object. """
        
        self.color1_channel: int
        """ the id of the color channel this object's color1 conforms to """
        self.color2_channel: int
        """ the id of the color channel this object's color2 conforms to """
        
        self.has_been_activated = False

    def __str__(self) -> str:
        if self.data:
            return f"LevelObject<{self.data.get('name')}>(x={self.x},y={self.y})"
        return f"(Empty) LevelObject(x={self.x},y={self.y})"
        
    def __getitem__(self, key):
        return self.data[key]     
    