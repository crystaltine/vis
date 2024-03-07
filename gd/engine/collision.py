from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.objects import LevelObject

class Collision:
    """
    Wrapper for objects that the player is currently touching, 
    
    Contains the object that the player is touching, and the side of the hitbox that the player  into.
    """
    
    def __init__(self, obj: 'LevelObject', vert_side: str = None, vert_coord: float = None): 
        """
        `obj` must be a dict directly from the `engine.objects.OBJECTS` dict.
        
        `vert_side` - optional: which vertical edge of the hitbox the player is touching.
        This should be among the values `["top", "bottom"]`, we dont care about left or right.
        Definition of "touching": within 0-CONSTANTS.SOLID_SURFACE_LENIENCY of an edge.
        
        `vert_coord` - req'd if vert_side: the y coordinate of the vertical edge of the hitbox the player is touching.
        This is used to adjust position of the player when they are touching a solid surface.
        
        The existence of this class is mainly to handle solid objects,
        since the player dies on some sides and walks on others (and the safe side depends on gravity)
        """
        
        self.obj = obj
        self.vert_side = vert_side
        self.vert_coord = vert_coord
        
        self.has_been_activated = False