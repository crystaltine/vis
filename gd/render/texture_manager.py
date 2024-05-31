from typing import Literal, TypedDict, TYPE_CHECKING
from PIL import Image
import numpy as np

from logger import Logger
from render.utils import mix_colors_opt as mco
from render.font import Font
from render.constants import CameraConstants

if TYPE_CHECKING:
    from level import Level, LevelObject

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
    
    bg_color: tuple = (24, 67, 240)
    """ Can change throughout the level using triggers. keep as rgb tuple. """
    ground_color: tuple = (8, 32, 170)
    """ Can change throughout the level using triggers. keep as rgb tuple. """
    
    player_color1: CameraConstants.RGBTuple = (111, 255, 83)
    player_color2: CameraConstants.RGBTuple = (90, 250, 255)
    player_icon_idx = 0
    player_icons = []
    """ A list of frames for the player icon. As of 2:43AM 29May2024, 
    this should be 4 frames, with 0=0deg rotation, 1=22.5, and so on. Only supports 4-way symmetry for now. """
    
    base_textures = {}
    texture_cache = {}
    """
    Caches transformed textures that we've seen before.
    
    Cache keys are stored in the following format:
    
    `{object name}_{rotation}_{reflection}_{color1|None}_{color2|None}`
    """
    
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

        pixels = np.array(np.array(im))
        colored_pixels: np.ndarray = np.zeros((len(pixels), len(pixels[0]), 4), dtype=np.uint8)

        for i in range(len(pixels)):
            for j in range(len(pixels[i])):
                
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

        pixels = np.array(np.array(im))
        
        # apply any changes
        
        final_pixels = np.rot90(pixels, ROTATION_VALUES[rotation])
        
        if reflections == CameraConstants.OBJECT_REFLECTIONS.VERTICAL.value:
            final_pixels = np.flipud(final_pixels)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.HORIZONTAL.value:
            final_pixels = np.fliplr(final_pixels)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.BOTH.value:
            final_pixels = np.flipud(np.fliplr(final_pixels))
        
        return final_pixels

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
        
        If a texture only needs one color, color1 will be used.
        If both colors are None, the texture will be returned as is.
        
        Color1 replaces darkness (black), color2 replaces brightness (white)
        """
        
        if color1 is None and color2 is None: return pixels
        if color1 is None: color1 = color2

        # create grayscale map, 0 ~ color1, 1 ~ color2
        
        alphas = pixels[:, :, 3]
        
        grayscale_weights = np.mean(pixels, axis=2) / 255
        grayscale_weights = grayscale_weights[:, :, np.newaxis]
        
        colorized = (1 - grayscale_weights) * color1 + grayscale_weights * color2
        
        # place the alpha channel back in
        colorized = np.concatenate((colorized, alphas[:, :, np.newaxis]), axis=2)
        
        return colorized
    
    def get_base_texture(object: "LevelObject") -> np.ndarray:
        """ Returns the base texture (no options like rotations, reflections, colorization applied) for a given LevelObject. """
        if TextureManager.base_textures.get(object.type) is None:
            raise ValueError(f"Base texture for object {object.type} not found.")
        
        return TextureManager.base_textures[object.type]
    
    def get_transformed_texture(level: "Level", object: "LevelObject") -> np.ndarray:
        """
        Given a `LevelObject`, attempts to search & return its specific texture in the cache.
        If not found, calculates the transformed texture of the object,
        with the correct rotation, reflection, and color (based on the object's color channel
        and what that color channel is currently set to in the `Level` object.
        
        Saves to texture cache. Returns the texture.
        """
        # search in cache
        transformed_key = TextureManager.get_transformed_key(level, object)
        cached = TextureManager.texture_cache.get(transformed_key)
        
        if cached is not None: 
            #Logger.log(f"[TextureManager/get_transformed_texture] Cache hit! key={transformed_key}")
            return cached
        
        # else, construct texture, save to cache, and return it
        # get base texture
        base_texture = TextureManager.get_base_texture(object)
        
        # apply all the stuff
        transformed_texture = TextureManager.reflect_texture(base_texture, object.reflection)
        transformed_texture = TextureManager.rotate_texture(transformed_texture, object.rotation)
        transformed_texture = TextureManager.colorize_texture(transformed_texture, *level.get_colors_of(object))
        
        TextureManager.texture_cache[transformed_key] = transformed_texture
        Logger.log(f"[TextureManager/get_transformed_texture] Saved new texture to cache: key={transformed_key}")
        return transformed_texture
    
    def get_transformed_key(level: "Level", object: "LevelObject") -> str:
        """
        Returns the "name" (key) that this object would have in the texture cache. 
        
        Format: 
        `{object name}_{rotation}_{reflection}_{color1|None}_{color2|None}`
        
        Level object is required as this function checks for the current
        color of the color channels that `object` is assigned to.
        """
        
        curr_color1, curr_color2 = level.get_colors_of(object)
        return f"{object.type}_{object.rotation}_{object.reflection}_{curr_color1}_{curr_color2}"
    
# preload all base textures
# load objects
TextureManager.base_textures.update({
    "spike": TextureManager.build_grayscale_texture_to_pixels("./assets/objects/spike.png"),
    "ground": TextureManager.build_colorful_texture_to_pixels("./assets/objects/ground.png"),
    "checkpoint": TextureManager.build_colorful_texture_to_pixels("./assets/objects/checkpoint.png"),
    "yellow_orb": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/orbs/orb_yellow.png"),
    "purple_orb": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/orbs/orb_purple.png"),
    "blue_orb": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/orbs/orb_blue.png"),
    "green_orb": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/orbs/orb_green.png"),
    "red_orb": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/orbs/orb_red.png"),
    "black_orb": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/orbs/orb_black.png"),
    "yellow_pad": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/pads/pad_yellow.png"),
    "purple_pad": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/pads/pad_purple.png"),
    "blue_pad": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/pads/pad_blue.png"),
    "red_pad": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/pads/pad_red.png"),
    "cube_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/mode_portals/mode_portal_cube.png"),
    "ship_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/mode_portals/mode_portal_ship.png"),
    "ball_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/mode_portals/mode_portal_ball.png"),
    "ufo_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/mode_portals/mode_portal_ufo.png"),
    "wave_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/mode_portals/mode_portal_wave.png"),
    "robot_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/mode_portals/mode_portal_robot.png"),
    "spider_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/mode_portals/mode_portal_spider.png"),
    "normal_grav_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/grav_portals/grav_portal_normal.png"),
    "reverse_grav_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/grav_portals/grav_portal_reverse.png"),
    "half_speed_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/speed_portals/speed_portal_half.png"),
    "normal_speed_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/speed_portals/speed_portal_normal.png"),
    "double_speed_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/speed_portals/speed_portal_double.png"),
    "triple_speed_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/speed_portals/speed_portal_triple.png"),
    "quadruple_speed_portal": TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/speed_portals/speed_portal_quadruple.png"),
})
TextureManager.base_textures.update({
    f"block0_{i}": TextureManager.build_grayscale_texture_to_pixels(f"./assets/objects/block0/{i}.png") for i in range(12)
})

# load player icons
TextureManager.player_icons = [
    TextureManager.build_grayscale_texture_to_pixels(f"./assets/icons/cubes/0/{i}.png", TextureManager.player_color1, TextureManager.player_color2)
    for i in range(4)
]

# load fonts
TextureManager.font_small1 = Font("./assets/fonts/small1.png")
TextureManager.font_title = Font("./assets/fonts/title.png")