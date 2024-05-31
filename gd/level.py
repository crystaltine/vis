from typing import List, Tuple, Dict, TYPE_CHECKING, Literal, TypedDict
from copy import deepcopy
import json

from logger import Logger
from gd_constants import GDConstants
from engine.objects import OBJECTS
from render.constants import CameraConstants

class StartSettings(TypedDict):
    bg_color: CameraConstants.RGBTuple
    ground_color: CameraConstants.RGBTuple
    position: Tuple[int, int]
    gamemode: GDConstants.gamemodes
    speed: GDConstants.speeds
    gravity: GDConstants.gravities
    default_color_channels: Dict[int, CameraConstants.RGBTuple]

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
LEVEL_TYPES: Dict[str, LevelMetadata] = {
    "official": OfficialLevelMetadata,
    "created": CreatedLevelMetadata,
    "online": OnlineLevelMetadata
}

class LevelParseError(Exception):
    pass

class Level:
    """ Class that contains helpful methods related to levels.
    Holds a 2D List of LevelObjects | Nones, and also metadata about the level. 
    The 2D list should also be rectangular - all rows should be the same length.
    """

    def __init__(self, metadata: LevelMetadata, leveldata: List[List["LevelObject"]]):
        self.metadata: LevelMetadata = metadata
        self.leveldata: List[List["LevelObject"]] = leveldata
        """ The backend level data. SHOULD be rectangular - see level_parser """
        
        self.length = len(leveldata[0])
        """ The length of the level in blocks. Equal to x-coord of the rightmost object + 1."""
        self.height = len(leveldata)
        """ The height of the level in blocks. Equal to y-coord of the highest object + 1. """
        
        self.color_channels: Dict[int, Tuple[int, int, int]] = {}
        """ Dict of id -> RGB color. Objects can reference these IDs to get their color. """
        
        self.bg_color = metadata["start_settings"]["bg_color"]
        self.ground_color = metadata["start_settings"]["ground_color"]
    
    @staticmethod
    def parse_from_file(filepath: str) -> "Level":
        """ Parses a level file (using the new JSON-based system) and returns a Level object."""
        
        levelfile: dict = ...
        
        with open(filepath, 'r') as f:
            levelfile = json.load(f)
            f.close()

        # parse metadata & check
        metadata: StartSettings = levelfile['metadata']
        level_type: str = metadata.get("type")

        level_metadata_format = LEVEL_TYPES.get(level_type)
        if level_metadata_format is None: 
            raise LevelParseError(f"Error while parsing level {filepath}: level type {level_type} is not supported.")

        required_keys = level_metadata_format.__required_keys__
        diff = required_keys.difference(metadata.keys())
        if len(diff) > 0:
            raise LevelParseError(f"Error while parsing level {filepath}: Missing the following metadata for level type {level_type}: {', '.join(diff)}")

        # metadata.start_settings should have ints as keys. JSON doesn't support int keys, so we need to convert them.
        metadata["start_settings"]["default_color_channels"] = {int(k): v for k, v in metadata["start_settings"]["default_color_channels"].items()}

        # parse leveldata into LevelObjects and Nones
        # recall that first row is highest row of the level
        leveldata: List[List["LevelObject"]] = []
        current_y_pos = len(levelfile['leveldata']) - 1
        for row in levelfile['leveldata']:
            # efficient way to iterate through list and convert all into LevelObject | Nones
            leveldata.append([LevelObject(obj, x, current_y_pos) if obj else None for x, obj in enumerate(row)])
            current_y_pos -= 1
        
        # pad leveldata to be rectangular (all rows the same length).
        max_leveldata_row_length = len(leveldata[0])
        for row in leveldata:
            max_leveldata_row_length = max(max_leveldata_row_length, len(row))

        for row in leveldata:
            len_diff = max_leveldata_row_length - len(row)
            if len_diff > 0:
                # pad with a lot of Nones
                row.extend([None] * len_diff)

        level = Level(metadata, leveldata)

        # parse & set default color channels    
        default_color_channels = metadata["start_settings"]["default_color_channels"]
        # assign default color channels to the level
        for channel_id, color in default_color_channels.items():
            level.set_color_channel(channel_id, color)
            
        return level
    
    parse = parse_from_file
    """ Alias for `parse_from_file` function. """
    
    def write_to_file(self, filepath: str) -> None:
        """ Writes the level in JSON format to a specified filepath, overwriting if the path already exists. """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': self.metadata,
                'leveldata': self.leveldata
            }, f)
    
    def get_object_at(self, x: int, y: int) -> "LevelObject | None":
        """
        Return a reference to the LevelObject at these specific coordinates.
        
        Remember that x=0,y=0 is the bottom left corner of a level, and that
        coordinates refer to the bottom left corner of a LevelObject.
        """
        
        row_index_in_list = len(self.leveldata) - y - 1
        return self.leveldata[row_index_in_list][x]
    
    def set_object_at(self, obj: "LevelObject", x: int, y: int) -> None:
        """
        Sets the object at coordinates x, y to `obj`.
        x and y must both be nonnegative.
        
        If out of range, expands the level.
        """
        # check for nonnegativitiy
        if x < 0 or y < 0:
            raise ValueError(f"Invalid position ({x},{y}) while trying to set object in level - both coordinates must be nonnegative.")
        
        if x > self.length:
            # expand level horizontally, add Nones as padding at the end of each row
            for row in self.leveldata:
                row.extend([None] * (x - self.length + 1))
                
            # update length field
            self.length += x - self.length + 1
        
        if y > self.height:
            # expand level vertically, add Nones as padding
            # note that to go higher, we add rows at the beginning
            new_rows = [[None] * self.length] * (y - self.height + 1)
            self.leveldata = new_rows + self.leveldata
            
            # update height field
            self.height += y - self.height + 1
        
        # set the new object    
        row_index_in_list = self.height - y - 1
        self.leveldata[row_index_in_list][x] = obj            
    
    def get_row(self, y: int, start: int = 0, end: int = None) -> List["LevelObject"]:
        """ Return a list of LevelObjects in a specific row, based on y-coordinate (remember, 0 is bottom row)
        Optionally can specify a start and end index to slice the row. If end is None, will go till the end of the row. """
        return self.leveldata[self.height - y - 1][start:end]
    
    def set_color_channel(self, id: int, new_color: CameraConstants.RGBTuple):
        """ Update the color of a color channel. Creates a new channel if it doesn't exist. """
        self.color_channels[id] = new_color
        
    def get_color_channel(self, id: int) -> CameraConstants.RGBTuple:
        """ Get the current color of a color channel. If the channel was never set, sets it to `(255, 255, 255)` (white) and returns that. """
        self.color_channels.setdefault(id, (255, 255, 255))
        return self.color_channels[id]
    
    def get_colors_of(self, object: "LevelObject") -> Tuple[CameraConstants.RGBTuple | None, CameraConstants.RGBTuple | None]:
        """
        Returns a tuple (color1, color2) of the colors a LevelObject currently has.
        
        For objects with only 1 or no color options (such as orbs not being able to be recolored)
        None will be returned as the corresponding tuple element.
        
        (For objects with a single color returns the color as the first element. The second will be None).
        """
        curr_color1 = self.get_color_channel(object.color1_channel) if object.color1_channel is not None else None
        curr_color2 = self.get_color_channel(object.color2_channel) if object.color2_channel is not None else None 
        
        return curr_color1, curr_color2      
        
class ObjectData(TypedDict):
    name: str
    hitbox_xrange: List[float]
    hitbox_yrange: List[float]
    hitbox_type: str
    collide_effect: str
    requires_click: bool
    
class LevelObjectDefSchema(TypedDict):
    """ The schema for levelobjects in the JSON level format. """
    type: str
    rotation: CameraConstants.OBJECT_ROTATIONS
    reflection: CameraConstants.OBJECT_REFLECTIONS
    color1_channel: int | None
    color2_channel: int | None

class LevelObject:
    """
    Represents a single object in a level. object types must be found in the `engine.objects.OBJECTS` dict.
    These should be created on level load, and NOT on every tick.
    
    Contains other data such as has_been_activated, position, (in the future, group, color, etc.)
    """
    def __init__(self, definition: LevelObjectDefSchema, x: float, y: float):
        
        # ensure all required keys are present
        required_keys = LevelObjectDefSchema.__required_keys__
        diff = required_keys.difference(definition.keys())
        if len(diff) > 0:
            raise LevelParseError(f"Error while creating LevelObject@({x},{y}): Missing the following keys: {', '.join(diff)}")
        
        self.type = definition["type"]
        """ The type/name of this object. e.g. 'block0_0', 'spike', 'yellow_orb'"""
        
        self.data: ObjectData = deepcopy(getattr(OBJECTS, self.type, None))
        """ Built-in backend data about the object, such as hitbox, collision effect, etc. """
        
        self.x: float = x
        """ Represents the x-position (left edge) of the object """
        self.y: float = y
        """ Represents the y-position (bottom edge) of the object """
        
        self.rotation: CameraConstants.OBJECT_ROTATIONS = definition["rotation"]
        """ Represents the rotation of the object, Can be 'up','right','down','left'. up = no rotation, right = 90deg to the right, etc. """
        self.reflection: CameraConstants.OBJECT_REFLECTIONS = definition["reflection"]
        """ Represents the reflection of the object. Can be 'none', 'horizontal', 'vertical', or 'both' """
        
        self.color1_channel: int | None = definition["color1_channel"]
        """ the id of the color channel this object's color1 (replaces dark) conforms to. Can be None if the object cannot be recolored. """
        self.color2_channel: int | None = definition["color2_channel"]
        """ the id of the color channel this object's color2 (replaces bright) conforms to. Can be None if the object only has 1 color."""
        
        self.has_been_activated = False
        """ flag for objects that can been activated by the player exactly once. """

    def __str__(self) -> str:
        if self.data:
            return f"LevelObject<{self.type}>(x={self.x},y={self.y})"
        return f"LevelObject<None>(x={self.x},y={self.y})"
        
    def __getitem__(self, key):
        return self.data[key]     
    