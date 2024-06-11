from typing import List, Tuple, Dict, TYPE_CHECKING, Literal, TypedDict, NotRequired
from copy import deepcopy
import json
from time import time

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
    default_color_channels: Dict[str, CameraConstants.RGBTuple]

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

    def __init__(
        self, 
        metadata: LevelMetadata, 
        color_trigger_locs: Dict[Tuple[int, int], Tuple[str | int, int, int, int]], 
        leveldata: List[List["LevelObject"]]):
        """ Programmatically construct a Level instance. If you're looking to parse from file, use Level.parse_from_file instead. """
        
        self.metadata: LevelMetadata = metadata
        self.leveldata: List[List["LevelObject"]] = leveldata
        """ The backend level data. SHOULD be rectangular - see level_parser """
        
        self.length = len(leveldata[0]) if len(leveldata) > 0 else 0
        """ The length of the level in blocks. Equal to x-coord of the rightmost object + 1."""
        self.height = len(leveldata)
        """ The height of the level in blocks. Equal to y-coord of the highest object + 1. """
        
        self.color_channels: Dict[int, Tuple[int, int, int]] = {}
        """ Dict of id -> RGB color. Objects can reference these IDs to get their color. """
        
        self.bg_color = tuple(metadata["start_settings"]["bg_color"])
        self.ground_color = tuple(metadata["start_settings"]["ground_color"])
        
        self.color_trigger_locs: Dict[Tuple[int, int], Tuple[str | int, int, int, int]] = color_trigger_locs
        """ A dict of (x, y) : (channel, r, g, b)) for efficiency in checking/activating color triggers. """
        self._ordered_color_trigger_locs: List[Tuple[int, int]] = []
        """ A list of color trigger locations, sorted with lower x-pos ones being last, that changes whenever a color trigger is passed 
        This optimizes the color trigger checking process so that we dont have to look at a huge number of objects every tick. """
        self.reset_color_trigger_cache()        
        
        self.filepath: str = ...
        """ Stores the filepath of the level. ONLY SET IF parse_from_file IS USED. """
    
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
        max_leveldata_row_length = len(leveldata[0]) if len(leveldata) > 0 else 0
        for row in leveldata:
            max_leveldata_row_length = max(max_leveldata_row_length, len(row))

        for row in leveldata:
            len_diff = max_leveldata_row_length - len(row)
            if len_diff > 0:
                # pad with a lot of Nones
                row.extend([None] * len_diff)
                
        # process color trigger locs
        # all the keys are stringified tuples. unstringify them.
        raw_color_trigger_locs = levelfile["color_trigger_locs"]
        
        # TODO - this is kinda dirty
        color_trigger_locs = {}
        for k, v in raw_color_trigger_locs.items():
            color_trigger_locs[tuple(map(int, k[1:-1].split(", ")))] = v

        level = Level(metadata, color_trigger_locs, leveldata)
        level.filepath = filepath

        # parse & set default color channels    
        default_color_channels = metadata["start_settings"]["default_color_channels"].copy()
        # assign default color channels to the level
        for channel_id, color in default_color_channels.items():
            level.set_color_channel(channel_id, color)
            
        return level
    
    parse = parse_from_file
    """ Alias for `parse_from_file` function. """
    
    def write_to_file(self, filepath: str) -> None:
        """ Writes the level in JSON format to a specified filepath, overwriting if the path already exists. """

        # convert self.leveldata into List[List[dict]] so it can be written back to a json file
        jsonized_leveldata = [[obj.to_json() if obj else None for obj in row] for row in self.leveldata]
        
        # cant store tuples as keys in JSON, so convert keys to stringified tuples
        color_trigger_locs = {str(k): v for k, v in self.color_trigger_locs.items()}
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': self.metadata,
                'color_trigger_locs': color_trigger_locs, # no need to convert this to JSON, it's already a dict
                'leveldata': jsonized_leveldata
            }, f)
    
    def reset_colors(self) -> None:
        #Logger.log(f"resetting bg color to {self.metadata['start_settings']['bg_color']}")
        #Logger.log(f"resetting ground color to {self.metadata['start_settings']['ground_color']}")
        self.bg_color = tuple(self.metadata["start_settings"]["bg_color"])
        self.ground_color = tuple(self.metadata["start_settings"]["ground_color"])
        self.color_channels = {int(k): v for k, v in self.metadata["start_settings"]["default_color_channels"].items()}
    
    def reset_color_trigger_cache(self) -> None:
        """ Resets the color trigger cache based on self.color_trigger_locs. """
        self._ordered_color_trigger_locs = sorted(self.color_trigger_locs.keys(), key=lambda x: x[0], reverse=True)
    
    def get_object_at(self, x: int, y: int) -> "LevelObject | None":
        """
        Return a reference to the LevelObject at these specific coordinates.
        
        Remember that x=0,y=0 is the bottom left corner of a level, and that
        coordinates refer to the bottom left corner of a LevelObject.
        
        Returns None if coordinates are out of bounds/negative.
        """
        
        row_index_in_list = len(self.leveldata) - y - 1
        
        if x < 0 or y < 0:
            return None
        
        if row_index_in_list >= len(self.leveldata) or x >= len(self.leveldata[row_index_in_list]):
            return None
        
        return self.leveldata[row_index_in_list][x]
    
    def set_object_at(self, x: int, y: int, obj: "LevelObject | AbstractLevelObject | None") -> None:
        """
        x and y must both be nonnegative. If x or y are greater than level length/height, expands the level.
        
        If obj is None, sets the object at coordinates x, y to None (delete object at that position)
        Will update any caches that change depending on the level data (such as color trigger cache)
        
        Otherwise:        
        Sets the object at coordinates x, y to a COPY of `obj`, converting
        it into a `LevelObject` and correctly setting its internally saved coordinates.
        """
        # check for nonnegativitiy
        if x < 0 or y < 0:
            raise ValueError(f"Invalid position ({x},{y}) while trying to set object in level - both coordinates must be nonnegative.")
        
        if x >= self.length:
            # expand level horizontally, add Nones as padding at the end of each row
            for row in self.leveldata:
                row.extend([None] * (x - self.length + 1))
                
            # update length field
            self.length += x - self.length + 1
        
        if y >= self.height:
            # expand level vertically, add Nones as padding
            # note that to go higher, we add rows at the beginning
            new_rows = [([None] * self.length) for _ in range(y - self.height + 1)]
            self.leveldata = new_rows + self.leveldata
            
            # update height field
            self.height += y - self.height + 1
        
        # set the new object    
        row_index_in_list = self.height - y - 1
        new_obj = LevelObject.copy_from(obj, x, y) if obj is not None else None
        
        if new_obj is None: # check if object being deleted is a color trigger
            if (x, y) in self.color_trigger_locs: # remove from color trigger cache
                del self.color_trigger_locs[(x, y)]      
                
        elif new_obj.type == "color_trigger": # sync color trigger cache if placing a color trigger
            self.color_trigger_locs[(x, y)] = (new_obj.color1_channel, 255, 255, 255)
    
        self.leveldata[row_index_in_list][x] = new_obj
    
    def check_color_triggers(self, player_x: float) -> None:
        """ Checks if the player x is past any color triggers in self._ordered_color_trigger_locs.
        If it is, activate the trigger and remove it from that cache, so it cant be activated again. """
        
        if len(self._ordered_color_trigger_locs) == 0:
            return
        
        #closest_trigger = self._ordered_color_trigger_locs[-1]
        # iterate backward through ordered color triggers. 
        # keep all the ones with the same x-value
        
        upcoming_triggers = [self._ordered_color_trigger_locs[-1]]
        for trigger in range(len(self._ordered_color_trigger_locs)-2, -1, -1):
            if self._ordered_color_trigger_locs[trigger][0] == upcoming_triggers[0][0]:
                upcoming_triggers.append(self._ordered_color_trigger_locs[trigger])
            else:
                break
        
        if player_x >= upcoming_triggers[0][0]: # player has passed the trigger line
            # activate all the upcoming color triggers
            
            #Logger.log(f">>>>>>> PLAYER PASSED TRIGGERS!!!!!! UPCOMING TRIGGERS len: {len(upcoming_triggers)}")
            
            for trigger_loc in upcoming_triggers:
                #Logger.log(f"trigger loc is {trigger_loc}, upcoming_triggers len={len(upcoming_triggers)}")
                self.set_color_channel(self.color_trigger_locs[trigger_loc][0], self.color_trigger_locs[trigger_loc][1:])
                #self.color_trigger_locs.pop(trigger_loc)
                self._ordered_color_trigger_locs.pop() # this SHOULD be fine since we ensure that upcoming_triggers is in the opposite order as _ordered_color_trigger_locs
    
    def get_row(self, y: int, start: int = 0, end: int = None) -> List["LevelObject"]:
        """ Return a list of LevelObjects in a specific row, based on y-coordinate (remember, 0 is bottom row)
        Optionally can specify a start and end index to slice the row. If end is None, will go till the end of the row. """
        return self.leveldata[self.height - y - 1][start:end]
    
    def set_color_channel(self, id: Literal["bg", "grnd"] | int, new_color: CameraConstants.RGBTuple):
        """ Update the color of a color channel. id must be int, "bg", or "grnd"
        Creates a new channel if it doesn't exist. """
        
        if id == "bg":
            self.bg_color = new_color
        elif id == "grnd":
            self.ground_color = new_color
        else:
            self.color_channels[id] = new_color
        
    def get_color_channel(self, id: Literal["bg", "grnd"] | int) -> CameraConstants.RGBTuple:
        """ Get the current color of a color channel. If the channel was never set, sets it to `(255, 255, 255)` (white) and returns that. """
        
        if id == "bg":
            return self.bg_color
        elif id == "grnd":
            return self.ground_color
        
        # else, assume numeric
        self.color_channels.setdefault(id, (255, 255, 255))
        return self.color_channels[id]
    
    def edit_color_trigger_at(self, x: int, y: int, new_channel: str | int, new_color: CameraConstants.RGBTuple) -> None:
        """ Edit the properties of a color trigger at a specific position (with new channel and color). 
        This function will do nothing if there is no color trigger at that position. """
        
        if (x, y) in self.color_trigger_locs:
            self.color_trigger_locs[(x, y)] = (new_channel, *new_color)
    
    def get_colors_of(self, object: "LevelObject") -> Tuple[CameraConstants.RGBTuple | None, CameraConstants.RGBTuple | None]:
        """
        Returns a tuple (color1, color2) of the colors a LevelObject currently has.
        
        For objects with only 1 or no color options (such as orbs not being able to be recolored)
        None will be returned as the corresponding tuple element.
        
        (For objects with a single color returns the color as the first element. The second will be None).
        """
        curr_color1 = self.get_color_channel(object.color1_channel) if object.color1_channel is not None else None
        curr_color2 = self.get_color_channel(object.color2_channel) if object.color2_channel is not None else None 
        
        #Logger.log(f"Level.get_colors_of: {object} has colors {curr_color1}, {curr_color2}")
        return curr_color1, curr_color2      
    
    def create_new_file(name: str) -> None:
        """ Creates a new (created-type) level file with the specified name, default metadata for everything else. """
    
        # default created level template is in ./levels/DEFAULT_CREATED_LEVEL.json
        default_data = json.load(f:=open("./levels/DEFAULT_CREATED_LEVEL.json", 'r'))
        f.close()
        
        default_data["metadata"]["name"] = name
        default_data["metadata"]["created_timestamp"] = time()
        default_data["metadata"]["modified_timestamp"] = time()
        
        # save it as a new file at ./levels/created/name.json
        new_filepath = f"./levels/created/{name}.json"
        json.dump(default_data, f2:=open(new_filepath, 'w'))
        f2.close()
    
class ObjectData(TypedDict):
    name: str
    hitbox_type: str
    color_channels: int
    invisible: bool | None # optional
    hitbox_xrange: List[float] | None # optional
    hitbox_yrange: List[float] | None # optional
    collide_effect: str | None # optional
    requires_click: bool | None # optional
    
class LevelObjectDefSchema(TypedDict):
    """ The schema for levelobjects in the JSON level format. """
    type: str
    rotation: CameraConstants.OBJECT_ROTATIONS
    reflection: CameraConstants.OBJECT_REFLECTIONS
    color1_channel: int | None
    color2_channel: int | None
    trigger_target: NotRequired[str | int | None] # optional - COLOR TRIGGERS ONLY
    trigger_color: NotRequired[CameraConstants.RGBTuple | None] # optional - COLOR TRIGGERS ONLY
    has_been_activated: NotRequired[bool | None] # optional - ACTIVATABLE OBJECTS ONLY

class LevelObject:
    """
    Represents a single object in a level. object types must be found in the `engine.objects.OBJECTS.MASTERLIST` dict.
    These should be created on level load, and NOT on every tick.
    
    Contains other data such as has_been_activated, position, (in the future, group, color, etc.)
    """
    def __init__(self, definition: LevelObjectDefSchema, x: float, y: float):
        
        # ensure all required keys are present
        required_keys = LevelObjectDefSchema.__required_keys__
        diff = required_keys.difference(definition.keys())
        if len(diff) > 0:
            raise LevelParseError(f"Error while creating LevelObject@({x},{y}): Missing the following keys: {', '.join(diff)}")
        
        self._ORIGINAL_DEFINITION = deepcopy(definition)
        
        self.type = definition["type"]
        """ The type/name of this object. e.g. 'block0_0', 'spike', 'yellow_orb'"""
        
        self.data: ObjectData = deepcopy(OBJECTS.get(self.type))
        """ Built-in backend data about the object, such as hitbox, collision effect, etc. """
        
        self.x: float = x
        """ Represents the x-position (left edge) of the object """
        self.y: float = y
        """ Represents the y-position (bottom edge) of the object """
        
        self.rotation: CameraConstants.OBJECT_ROTATIONS = definition["rotation"]
        """ Represents the rotation of the object, Can be 'up','right','down','left'. up = no rotation, right = 90deg to the right, etc. """
        self.reflection: CameraConstants.OBJECT_REFLECTIONS = definition["reflection"]
        """ Represents the reflection of the object. Can be 'none', 'horizontal', 'vertical', or 'both' """
        
        self.color1_channel: int | None = definition["color1_channel"] if self.data["color_channels"] > 0 else None
        """ the id of the color channel this object's color1 (replaces dark) conforms to. Can be None if the object cannot be recolored. """
        self.color2_channel: int | None = definition["color2_channel"] if self.data["color_channels"] > 1 else None
        """ the id of the color channel this object's color2 (replaces bright) conforms to. Can be None if the object only has 1 color."""
        
        self.trigger_target: str | int | None = definition.get("trigger_target") or "bg"
        """ the id of the object this color trigger will activate. """
        
        self.trigger_color: CameraConstants.RGBTuple | None = definition.get("trigger_color") or (255, 255, 255)
        """ the color this color trigger will activate with. """
        
        self.has_been_activated = False
        """ flag for objects that can been activated by the player exactly once. """

    def __str__(self) -> str:
        return f"LevelObject(type={self.type},x={self.x},y={self.y})"
    
    def copy_from(other: "AbstractLevelObject | LevelObject", x: float, y: float) -> "LevelObject":
        """ Creates a new LevelObject with the same data as another object, but at a different position. """
        # can we use __dict__ here?
        new = LevelObject(other._ORIGINAL_DEFINITION, x, y)
        # set other fields in case they were changed after definition
        new.type = other.type
        new.data = other.data
        new.rotation = other.rotation
        new.reflection = other.reflection
        new.color1_channel = other.color1_channel
        new.color2_channel = other.color2_channel
        new.has_been_activated = other.has_been_activated
        new.trigger_target = other.trigger_target
        new.trigger_color = other.trigger_color
        
        return new
        
    def abstract_copy(self) -> "AbstractLevelObject":
        """ Returns a copy of this LevelObject as an AbstractLevelObject. (no specific position) """
        new = AbstractLevelObject(self._ORIGINAL_DEFINITION)
        # set other fields in case they were changed after definition
        new.type = self.type
        new.data = self.data
        new.rotation = self.rotation
        new.reflection = self.reflection
        new.color1_channel = self.color1_channel
        new.color2_channel = self.color2_channel
        new.has_been_activated = self.has_been_activated
        new.trigger_target = self.trigger_target
        new.trigger_color = self.trigger_color
        
        return new
    
    def rotate(self, direction: Literal["clockwise", "counterclockwise"]) -> None:
        """ Rotates the object 90 degrees clockwise or counterclockwise. """
        # note: can clean this up if we use number-based rotation instead of strings
        if direction == "clockwise":
            self.rotation = CameraConstants.ROTATIONS_CLOCKWISE[self.rotation]
        elif direction == "counterclockwise":
            self.rotation = CameraConstants.ROTATIONS_COUNTERCLOCKWISE[self.rotation]
            
    def reflect(self, direction: Literal["horizontal", "vertical", "both"]) -> None:
        """ Reflects the object across a certain axis. """
        
        match direction:
            case "horizontal":
                self.reflection = CameraConstants.REFLECTIONS_HORIZONTAL[self.reflection]
            case "vertical":
                self.reflection = CameraConstants.REFLECTIONS_VERTICAL[self.reflection]
            case "both":
                self.reflection = CameraConstants.REFLECTIONS_BOTH[self.reflection]
    
    def to_json(self) -> dict:
        """ 
        Converts this levelobject to a dict (json-like). Loses information about position, but
        this format is compatible to be stored inside leveldata files. 
        
        Example LevelObject JSON:
        ```json
        {
            "type": "mode_portal_ufo",
            "rotation": "up",
            "reflection": "none",
            "color1_channel": null,
            "color2_channel": null,
            "trigger_target": "bg",
            "trigger_color": [255, 255, 255],
        }
        """
        return {
            "type": self.type,
            "rotation": self.rotation,
            "reflection": self.reflection,
            "color1_channel": self.color1_channel,
            "color2_channel": self.color2_channel,
            "trigger_target": self.trigger_target,
            "trigger_color": self.trigger_color
        }

class AbstractLevelObject: # not inheriting since all functions are different lol
    """
    Represents an abstract object, with no position. Object types must be found in the `engine.objects.OBJECTS.MASTERLIST` dict.
    This is pretty much exactly the same as LevelObject, just missing x and y fields.
    
    Contains other data such as has_been_activated, position, (in the future, group, color, etc.)
    """
    def __init__(self, definition: LevelObjectDefSchema):
        
        # ensure all required keys are present
        required_keys = LevelObjectDefSchema.__required_keys__
        diff = required_keys.difference(definition.keys())
        if len(diff) > 0:
            raise LevelParseError(f"Error while creating AbstractLevelObject: Missing the following keys: {', '.join(diff)}")
        
        self._ORIGINAL_DEFINITION = deepcopy(definition)
        
        self.type = definition["type"]
        """ The type/name of this object. e.g. 'block0_0', 'spike', 'yellow_orb'"""
        
        self.data: ObjectData = deepcopy(OBJECTS.get(self.type))
        """ Built-in backend data about the object, such as hitbox, collision effect, etc. """
        
        self.rotation: CameraConstants.OBJECT_ROTATIONS = definition["rotation"]
        """ Represents the rotation of the object, Can be 'up','right','down','left'. up = no rotation, right = 90deg to the right, etc. """
        self.reflection: CameraConstants.OBJECT_REFLECTIONS = definition["reflection"]
        """ Represents the reflection of the object. Can be 'none', 'horizontal', 'vertical', or 'both' """
        
        self.color1_channel: int | None = definition["color1_channel"]
        """ the id of the color channel this object's color1 (replaces dark) conforms to. Can be None if the object cannot be recolored. """
        self.color2_channel: int | None = definition["color2_channel"]
        """ the id of the color channel this object's color2 (replaces bright) conforms to. Can be None if the object only has 1 color."""
        
        self.trigger_target: str | int | None = definition.get("trigger_target") or "bg"
        """ the id of the object this color trigger will activate. """
        
        self.trigger_color: CameraConstants.RGBTuple | None = definition.get("trigger_color") or (255, 255, 255)
        """ the color this color trigger will activate with. """
        
        self.has_been_activated = False
        """ flag for objects that can been activated by the player exactly once. """

    def __str__(self) -> str:
        return f"AbstractLevelObject(type={self.type})"
    
    def rotate(self, direction: Literal["clockwise", "counterclockwise"]) -> None:
        """ Rotates the object 90 degrees clockwise or counterclockwise. """
        # note: can clean this up if we use number-based rotation instead of strings
        if direction == "clockwise":
            self.rotation = CameraConstants.ROTATIONS_CLOCKWISE[self.rotation]
        elif direction == "counterclockwise":
            self.rotation = CameraConstants.ROTATIONS_COUNTERCLOCKWISE[self.rotation]
            
    def reflect(self, direction: Literal["horizontal", "vertical", "both"]) -> None:
        """ Reflects the object across a certain axis. """
        
        match direction:
            case "horizontal":
                self.reflection = CameraConstants.REFLECTIONS_HORIZONTAL[self.reflection]
            case "vertical":
                self.reflection = CameraConstants.REFLECTIONS_VERTICAL[self.reflection]
            case "both":
                self.reflection = CameraConstants.REFLECTIONS_BOTH[self.reflection]
