from typing import Literal, Dict, List, TypedDict, TYPE_CHECKING
from PIL import Image
import numpy as np

from gd_constants import GDConstants
from logger import Logger
from render.utils import mix_colors_opt as mco
from render.font import Font
from render.constants import CameraConstants
from level import Level, LevelObject, AbstractLevelObject
from engine.objects import OBJECTS

if TYPE_CHECKING:
    from engine.player import Player

ROTATION_VALUES = {
    CameraConstants.OBJECT_ROTATIONS.UP.value: 0,
    CameraConstants.OBJECT_ROTATIONS.LEFT.value: 1,
    CameraConstants.OBJECT_ROTATIONS.DOWN.value: 2,
    CameraConstants.OBJECT_ROTATIONS.RIGHT.value: 3
}

class GrayscaleTextureOptions(TypedDict):
    color1: str | tuple
    color2: str | tuple
    scale: int
    rotation: CameraConstants.OBJECT_ROTATIONS
    reflections: CameraConstants.OBJECT_REFLECTIONS
    
class ColorfulTextureOptions(TypedDict):
    scale: int
    rotation: CameraConstants.OBJECT_ROTATIONS
    reflections: CameraConstants.OBJECT_REFLECTIONS

class TextureManager:
    
    player_color1: CameraConstants.RGBTuple = (111, 255, 83)
    player_color2: CameraConstants.RGBTuple = (90, 250, 255)
    player_icons: Dict[str, List[np.ndarray]] = {}
    """ A dict of gamemode : list of frames for player icon. Cube has 4 frames, ball has 2, ufo has 1. """
    
    base_textures = {}
    texture_cache = {}
    """
    Caches transformed textures that we've seen before.
    
    Cache keys are stored in the following format:
    
    `{object name}_{rotation}_{reflection}_{color1|None}_{color2|None}`
    """
    
    # currently unused
    ground_texture_cache = {}
    """ Cache for ground textures.
    Key is color, value is a list of CameraConstants.GROUND_TEXTURE_PERIOD textures that correspond to the different offsets."""
    
    # load fonts
    font_small1 = Font("./assets/fonts/small1.png")
    font_title = Font("./assets/fonts/title.png")
    
    DEFAULT_GRAYSCALE_TEXTURE_OPTIONS: GrayscaleTextureOptions = {
        "color1": (0, 0, 0),
        "color2": (255, 255, 255),
        "scale": 1,
        "rotation": CameraConstants.OBJECT_ROTATIONS.UP,
        "reflections": CameraConstants.OBJECT_REFLECTIONS.NONE
    }
    DEFAULT_COLORFUL_TEXTURE_OPTIONS: ColorfulTextureOptions = {
        "scale": 1,
        "rotation": CameraConstants.OBJECT_ROTATIONS.UP,
        "reflections": CameraConstants.OBJECT_REFLECTIONS.NONE
    }

    def build_grayscale_texture_to_pixels(
        filepath: str,
        color1: CameraConstants.RGBTuple = (0, 0, 0),
        color2: CameraConstants.RGBTuple = (255, 255, 255),
        scale: int = 1,
        rotation: CameraConstants.OBJECT_ROTATIONS = "up",
        reflections: CameraConstants.OBJECT_REFLECTIONS = "none"
        ) -> np.ndarray:
        """
        Internal function for "compiling" a texture from a grayscale image. (applies colors, scale, rotation, reflections)
        Turns the png file to a 2d list of pixel objects (rgba np arrays) (see ./camera_frame.py)
        """
        
        im = Image.open(filepath)
        
        # apply scaling if necessary
        if scale != 1:
            if not isinstance(scale, int): raise ValueError("[render texture grayscale]: scale must be an integer")
            im = im.resize((im.width * scale, im.height * scale))

        pixels = np.array(im)
        colored_pixels: np.ndarray = np.zeros((len(pixels), len(pixels[0]), 4), dtype=np.uint8)

        for i in range(len(pixels)):
            for j in range(len(pixels[i])):
                
                # NOTE - this is slow, and there are vectorized ways to do this
                
                px_data = pixels[i][j] # should be a 4-long ndarray of the rgba values
                alpha = px_data[3] if len(px_data) == 4 else 255

                # find the grayscale values of the pixel (average of rgb).
                # with the grayscale % (0-100) where 0 is black and 100 is white,
                # use a color mix between the edge color and bg color
                # 0 is edge color, 100 is bg color
                
                gray = sum(px_data[0:3]) / 3 / 255
                
                colored_px = mco(color1, color2, gray)
                colored_pixels[i][j] = (*colored_px, alpha) # insert original alpha back in
        
        # apply any changes
        final_pixels = np.rot90(colored_pixels, ROTATION_VALUES[rotation])
        
        if reflections == CameraConstants.OBJECT_REFLECTIONS.VERTICAL.value:
            final_pixels = np.flipud(final_pixels)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.HORIZONTAL.value:
            final_pixels = np.fliplr(final_pixels)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.BOTH.value:
            final_pixels = np.flipud(np.fliplr(final_pixels))
            
        return final_pixels

    def build_colorful_texture_to_pixels(
        filepath: str,
        scale: int = 1,
        rotation: Literal["up", "right", "down", "left"] = "up",
        reflections: Literal["none", "vert", "horiz", "both"] = "none"
        ) -> np.ndarray:
        """
        Internal function for "compiling" a texture from a colorful image. (applies scale, rotation, reflections)
        Turns the png file to a 2d list of pixel objects (rgba np arrays) (see ./camera_frame.py)
        """
        
        im = Image.open(filepath)
        
        # apply scaling if necessary
        if scale != 1:
            if not isinstance(scale, int): raise ValueError("[render texture grayscale]: scale must be an integer")
            im = im.resize((im.width * scale, im.height * scale))

        pixels = np.array(im)
        
        # apply any changes
        
        final_pixels = np.rot90(pixels, ROTATION_VALUES[rotation])
        
        if reflections == CameraConstants.OBJECT_REFLECTIONS.VERTICAL.value:
            final_pixels = np.flipud(final_pixels)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.HORIZONTAL.value:
            final_pixels = np.fliplr(final_pixels)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.BOTH.value:
            final_pixels = np.flipud(np.fliplr(final_pixels))
        
        return final_pixels
    
    def compile_texture(filepath: str) -> np.ndarray:
        """ Basically build_grayscale_texture_to_pixels or build_colorful_texture_to_pixels but without any options,
        since those seem pretty useless lol """
        return np.array(Image.open(filepath))

    def reflect_texture(pixels: np.ndarray, reflection: CameraConstants.OBJECT_REFLECTIONS) -> np.ndarray:
        """
        Reflects a texture horizontally, vertically, or both.
        """
        
        if reflection == CameraConstants.OBJECT_REFLECTIONS.VERTICAL.value:
            return np.flipud(pixels)
        elif reflection == CameraConstants.OBJECT_REFLECTIONS.HORIZONTAL.value:
            return np.fliplr(pixels)
        elif reflection == CameraConstants.OBJECT_REFLECTIONS.BOTH.value:
            return np.flipud(np.fliplr(pixels))
        else:
            return pixels
        
    def rotate_texture(pixels: np.ndarray, rotation: CameraConstants.OBJECT_ROTATIONS) -> np.ndarray:
        """
        Rotates a texture 0, 90, 180, or 270 degrees.
        """
        return np.rot90(pixels, ROTATION_VALUES[rotation])
    
    def colorize_texture(pixels: np.ndarray, color1: CameraConstants.RGBTuple | None, color2: CameraConstants.RGBTuple | None) -> np.ndarray:
        """
        Given a texture, colorizes it with the two colors specified.
        Uses numpy vectorization so should be kinda fast.
        
        If a texture only needs one color, color1 will be used. Please pass color2 = None in this case.
        If both colors are None, the texture will be returned as is.
        
        Color1 replaces darkness (black), color2 replaces brightness (white)
        """
        
        if color1 is None and color2 is None: return pixels

        # create grayscale map, 0 ~ color1, 1 ~ color2
        
        # if pixels doesn't have an alpha channel, add one
        if pixels.shape[2] == 3:
            pixels = np.concatenate((pixels, np.full((pixels.shape[0], pixels.shape[1], 1), 255, dtype=np.uint8)), axis=2)
        
        alphas = pixels[:, :, 3]
        
        grayscale_weights = np.mean(pixels[:, :, :3], axis=2) / 255
        grayscale_weights = grayscale_weights[:, :, np.newaxis]
        
        colorized = ...
        if color2 is None: # single-colored objects
            colorized = (grayscale_weights) * color1
        else:
            colorized = (1 - grayscale_weights) * color1 + grayscale_weights * color2
        
        # place the alpha channel back in
        colorized = np.concatenate((colorized, alphas[:, :, np.newaxis]), axis=2)
        
        return colorized
    
    def set_transparency(pixels: np.ndarray, alpha: int) -> np.ndarray:
        """ Sets the alpha channel of a texture to a specific value. `alpha` should be from 0 to 255 inclusive.
        Mixes alpha values if image is already transparent.
        """
        
        # if pixels doesn't have an alpha channel, add one
        if pixels.shape[2] == 3:
            pixels = np.concatenate((pixels, np.full((pixels.shape[0], pixels.shape[1], 1), 255, dtype=np.uint8)), axis=2)
            return
        
        orig_alpha = pixels[:, :, 3]
        pixels[:, :, 3] = alpha * (orig_alpha / 255)
        #Logger.log_on_screen(GDConstants.term, f"[TextureManager/set_transparency] Set a={alpha}.")
        return pixels
    
    def get_base_texture(object: "LevelObject | AbstractLevelObject", hide_invis: bool = False) -> np.ndarray:
        """ 
        Returns the base texture (no options like rotations, reflections, colorization applied)
        for a given LevelObject | AbstractLevelObject. If hide_invis is True, returns a blank texture if the object is invisible. """
        if TextureManager.base_textures.get(object.type) is None:
            raise ValueError(f"Base texture for object {object.type} not found.")
        
        if hide_invis and object.data.get("invisible", False):
            return np.zeros((1, 1, 4), dtype=np.uint8)
        else:    
            return TextureManager.base_textures[object.type].copy()
    
    def get_transformed_texture(level: "Level", object: "LevelObject | AbstractLevelObject", hide_invis: bool = False) -> np.ndarray:
        """
        Given a `LevelObject` or `AbstractLevelObject`, attempts to search & return its specific texture in the cache.
        If not found, calculates the transformed texture of the object,
        with the correct rotation, reflection, and color (based on the object's color channel
        and what that color channel is currently set to in the `Level` object.
        
        Saves to texture cache. Returns the texture.
        """
        
        if hide_invis and object.data.get("invisible"):
            return np.zeros((1, 1, 4), dtype=np.uint8)
        
        # if object is trigger (cant be rotated/reflected) return ase
        if object.type == "color_trigger": # TODO - this is very hacky
            return TextureManager.get_base_texture(object).copy()
        
        # search in cache
        transformed_key = TextureManager.get_transformed_key(level, object)
        cached = TextureManager.texture_cache.get(transformed_key)
        
        if cached is not None: 
            #Logger.log(f"[TextureManager/get_transformed_texture] Cache hit! key={transformed_key}, object={object}")
            return cached.copy()
        
        # else, construct texture, save to cache, and return it
        # get base texture
        base_texture = TextureManager.get_base_texture(object)
        
        #if isinstance(object, AbstractLevelObject):
        #    return base_texture.copy()
        
        # apply all the stuff
        transformed_texture = TextureManager.reflect_texture(base_texture, object.reflection)
        transformed_texture = TextureManager.rotate_texture(transformed_texture, object.rotation)
        transformed_texture = TextureManager.colorize_texture(transformed_texture, *level.get_colors_of(object))
        
        TextureManager.texture_cache[transformed_key] = transformed_texture
        #Logger.log(f"[TextureManager/get_transformed_texture] Saved new texture to cache: key={transformed_key}")
        return transformed_texture.copy()
    
    def get_transformed_key(level: "Level", object: "LevelObject | AbstractLevelObject") -> str:
        """
        Returns the "name" (key) that this object would have in the texture cache. 
        
        Format: 
        `{object name}_{rotation}_{reflection}_{color1|None}_{color2|None}`
        
        Level object is required as this function checks for the current
        color of the color channels that `object` is assigned to.
        """
        
        curr_color1, curr_color2 = level.get_colors_of(object)
        return f"{object.type}_{object.rotation}_{object.reflection}_{curr_color1}_{curr_color2}"
    
    def get_curr_player_icon(player: "Player") -> np.ndarray:
        """ Returns the current player icon based on the player's current rotation. """
        return TextureManager.player_icons[player.gamemode][player.get_animation_frame_index()]
    
    def get_curr_ground_texture(level: "Level", player_x: float) -> np.ndarray:
        """ Returns current ground texture, recolored and offset based on the player's position and level colors. """
        
        ground_offset = round(player_x*CameraConstants.BLOCK_WIDTH)%CameraConstants.GROUND_TEXTURE_PERIOD
        
        # ground texture cache system, disabled cuz it wasnt working and not using a cache is fine cuz its numpy...
        #Logger.log(f"player dist from start={player.get_dist_from_start()}: offset={ground_offset}")
        
        #ground_color = tuple(level.ground_color)
        
        # try to find in cache
        #cached_list = TextureManager.ground_texture_cache.get(ground_color)
        #if cached_list is None:
        #    TextureManager.ground_texture_cache[ground_color] = [] # init cache list
        #else: # cache list exists, but index might not
        #    if ground_offset < len(cached_list):
        #        # cache hit!
        #        Logger.log(f"ground offset: {ground_offset}, len: {len(cached_list)}")
        #        return cached_list[ground_offset].copy()
            
        # not found in cache, calculate and save
        
        recolored_ground = TextureManager.colorize_texture(TextureManager.base_textures["ground"].copy(), level.ground_color, None)
    
        # the ground texture is periodic with period CameraConstants.GROUND_TEXTURE_PERIOD px. 
        # calculate player position in px, mod ^^, and offset the texture by that amount
        recolored_ground = np.roll(recolored_ground, -ground_offset, axis=1)
        #TextureManager.ground_texture_cache[ground_color].append(recolored_ground)
        
        return recolored_ground
    
####### preload all objects' base textures
for object_name in OBJECTS.MASTERLIST:
    TextureManager.base_textures.update({
        object_name: TextureManager.compile_texture(OBJECTS.MASTERLIST[object_name]["texture_path"])
    })

##### Special non-object texture loading
TextureManager.base_textures.update({
    "ground": TextureManager.compile_texture("./assets/objects/general/ground.png"),
    "checkpoint": TextureManager.compile_texture("./assets/objects/general/checkpoint.png"),
})

# load player icons
TextureManager.player_icons['cube'] = [
    TextureManager.build_grayscale_texture_to_pixels(
        f"./assets/icons/cube/0/{i}.png", 
        TextureManager.player_color1, 
        TextureManager.player_color2
    ) for i in range(4)
]
TextureManager.player_icons['ball'] = [
    TextureManager.build_grayscale_texture_to_pixels(
        f"./assets/icons/ball/0/{i}.png", 
        TextureManager.player_color1, 
        TextureManager.player_color2
    ) for i in range(2)
]
TextureManager.player_icons['ufo'] = [
    TextureManager.build_grayscale_texture_to_pixels(
        f"./assets/icons/ufo/0/0.png", 
        TextureManager.player_color1, 
        TextureManager.player_color2
    )
]
TextureManager.player_icons['wave'] = [
    TextureManager.build_grayscale_texture_to_pixels(
        f"./assets/icons/wave/0/{i}.png", 
        TextureManager.player_color1, 
        TextureManager.player_color2
    ) for i in range(3)
]