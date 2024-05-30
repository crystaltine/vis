from typing import List, Tuple, Literal, TypedDict, TYPE_CHECKING
from PIL import Image
import numpy as np
import traceback

from logger import Logger
from render.utils import fc, mix_colors, mix_colors_opt as mco
from render.font import Font
from render.constants import CameraConstants

if TYPE_CHECKING:
    from level import Level, LevelObject

ROTATION_VALUES = {
    CameraConstants.OBJECT_ROTATIONS.UP: 0,
    CameraConstants.OBJECT_ROTATIONS.RIGHT: 1,
    CameraConstants.OBJECT_ROTATIONS.DOWN: 2,
    CameraConstants.OBJECT_ROTATIONS.LEFT: 3
}

class GrayscaleTextureOptions(TypedDict):
    replace_dark_with: str | tuple
    replace_light_with: str | tuple
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
    
    textures = {}
    texture_cache = {} # TODO
    """
    Caches transformed textures that we've seen before.
    
    Cache keys are stored in the following format:
    
    `{object name}_{rotation}_{reflection}_{color1 hex|None}_{color2 hex|None}`
    """
    
    def get_texture(texture_name: str):
        return TextureManager.textures[texture_name]
    
    def get_cached_texture(object_name: str, object_options: dict):
        pass # TODO

    DEFAULT_GRAYSCALE_TEXTURE_OPTIONS: GrayscaleTextureOptions = {
        "replace_dark_with": (0, 0, 0),
        "replace_light_with": (255, 255, 255),
        "scale": 1,
        "rotation": CameraConstants.OBJECT_ROTATIONS.UP,
        "reflections": CameraConstants.OBJECT_REFLECTIONS.NONE
    }
    DEFAULT_COLORFUL_TEXTURE_OPTIONS: ColorfulTextureOptions = {
        "scale": 1,
        "rotation": CameraConstants.OBJECT_ROTATIONS.UP,
        "reflections": CameraConstants.OBJECT_REFLECTIONS.NONE
    }

    # should be unused due to new rendering system not needing chars
    def build_grayscale_texture(
        filepath: str,
        replace_dark_with: str | tuple = "#000000",
        replace_light_with: str | tuple = "#ffffff",
        scale: int = 1,
        rotation: CameraConstants.OBJECT_ROTATIONS = "up",
        reflections: CameraConstants.OBJECT_REFLECTIONS = "none",
        transparency_color: str | tuple = None) -> list[str]:
        """
        Internal function for "compiling" a texture from a grayscale image. (applies colors, scale, rotation, reflections)
        Basically turns a png file into a list of str, where each element is "▀" with some ANSI formatting applied (for color)
        
        ## New! - transparency support! Pass in transparency_color as a hexcode (preferably) to render alpha on top of it.
        If `transparency_color` is None, the current bg color (`TextureManager.replace_light_with`) will be used.
        """
        
        im = Image.open(filepath)
        transparency_color = replace_light_with if transparency_color is None else transparency_color
        
        # apply scaling if necessary
        if scale != 1:
            if not isinstance(scale, int): raise ValueError("[render texture grayscale]: scale must be an integer")
            im = im.resize((im.width * scale, im.height * scale))

        pixels = np.array(np.array(im))
        final_chars: List[List[str]] = []
        for i in range(0, len(pixels)-1, 2): # TODO - last row of odd height images is not being processed
            row = pixels[i]
            row2 = pixels[i + 1]
            
            final_row: List[str] = []
            
            for j in range(len(row)):
                top_pixel = row[j]
                bottom_pixel = row2[j]
                
                # find the grayscale values of the pixel (average of rgb).
                # with the grayscale % (0-100) where 0 is black and 100 is white,
                # use a color mix between the edge color and bg color
                # 0 is edge color, 100 is bg color
                
                top_px_gray = sum(top_pixel[0:3]) / 3 / 255
                bottom_px_gray = sum(bottom_pixel[0:3]) / 3 / 255
                
                top_px_alpha = top_pixel[3] / 255
                bottom_px_alpha = bottom_pixel[3] / 255
                
                top_px_midtone = mix_colors(transparency_color, mix_colors(replace_dark_with, replace_light_with, top_px_gray), top_px_alpha)
                bottom_px_midtone = mix_colors(transparency_color, mix_colors(replace_dark_with, replace_light_with, bottom_px_gray), bottom_px_alpha)
                
                final_row.append(f"\x1b[0m{fc(fg=top_px_midtone, bg=bottom_px_midtone)}▀")
                
            final_chars.append(final_row)
        
        final_chars = np.array(final_chars)
        
        # apply any changes
        final_chars = np.rot90(final_chars, ROTATION_VALUES[rotation])
        
        if reflections == CameraConstants.OBJECT_REFLECTIONS.VERTICAL:
            final_chars = np.flipud(final_chars)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.HORIZONTAL:
            final_chars = np.fliplr(final_chars)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.BOTH:
            final_chars = np.flipud(np.fliplr(final_chars))
            
        return ["".join(row) for row in final_chars]
    
    def build_grayscale_texture_to_pixels(
        filepath: str,
        replace_dark_with: CameraConstants.RGBTuple = (0, 0, 0),
        replace_light_with: CameraConstants.RGBTuple = (255, 255, 255),
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
                
                colored_px = mco(replace_dark_with, replace_light_with, gray)
                colored_pixels[i][j] = (*colored_px, alpha) # insert original alpha back in
        
        # apply any changes
        final_pixels = np.rot90(colored_pixels, ROTATION_VALUES[rotation])
        
        if reflections == CameraConstants.OBJECT_REFLECTIONS.VERTICAL:
            final_pixels = np.flipud(final_pixels)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.HORIZONTAL:
            final_pixels = np.fliplr(final_pixels)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.BOTH:
            final_pixels = np.flipud(np.fliplr(final_pixels))
            
        return final_pixels

    # should be unused due to new rendering system not needing chars
    def build_colorful_texture(
        filepath: str,
        scale: int = 1,
        rotation: Literal["up", "right", "down", "left"] = "up",
        reflections: Literal["none", "vert", "horiz", "both"] = "none",
        transparency_color: str | tuple = None) -> list[str]:
        """
        Internal function for "compiling" a texture from a colorful image. (applies scale, rotation, reflections)
        The same as build_grayscale_texture, but does not take in replace_dark_with and replace_light_with, and instead uses the colors from the image.
        Basically turns a png file into a list of str, where each element is "▀" with some ANSI formatting applied (for color)
        
        ## New! - transparency support! Pass in transparency_color as a hexcode (preferably) to render alpha on top of it.
        If `transparency_color` is None, the current bg color (`TextureManager.replace_light_with`) will be used.
        """
        
        im = Image.open(filepath)
        transparency_color = TextureManager.replace_light_with if transparency_color is None else transparency_color
        
        # apply scaling if necessary
        if scale != 1:
            if not isinstance(scale, int): raise ValueError("[render texture colorful]: scale must be an integer")
            im = im.resize((im.width * scale, im.height * scale))

        pixels = np.array(np.array(im))
        final_chars: List[List[str]] = []
        for i in range(0, len(pixels)-1, 2): # TODO - last row of odd height images is not being processed
            row = pixels[i]
            row2 = pixels[i + 1]
            
            final_row: List[str] = []
            
            for j in range(len(row)):
                top_pixel = row[j]
                bottom_pixel = row2[j]
                
                top_px_alpha = top_pixel[3] / 255
                bottom_px_alpha = bottom_pixel[3] / 255
                
                top_px_final_color = mix_colors(transparency_color, top_pixel[0:3], top_px_alpha)
                bottom_px_final_color = mix_colors(transparency_color, bottom_pixel[0:3], bottom_px_alpha)
                
                final_row.append(f"\x1b[0m{fc(fg=top_px_final_color, bg=bottom_px_final_color)}▀")
                
            final_chars.append(final_row)
        
        final_chars = np.array(final_chars)
        
        # apply any changes
        final_chars = np.rot90(final_chars, ROTATION_VALUES[rotation])
        
        if reflections == CameraConstants.OBJECT_REFLECTIONS.VERTICAL:
            final_chars = np.flipud(final_chars)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.HORIZONTAL:
            final_chars = np.fliplr(final_chars)
        elif reflections == CameraConstants.OBJECT_REFLECTIONS.BOTH:
            final_chars = np.flipud(np.fliplr(final_chars))
            
        return ["".join(row) for row in final_chars]

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
        
        if reflections == CameraConstants.OBJECT_REFLECTIONS.VERTICAL:
            final_pixels = np.flipud(final_pixels)
        elif reflections ==  CameraConstants.OBJECT_REFLECTIONS.HORIZONTAL:
            final_pixels = np.fliplr(final_pixels)
        elif reflections ==  CameraConstants.OBJECT_REFLECTIONS.BOTH:
            final_pixels = np.flipud(np.fliplr(final_pixels))
        
        return final_pixels

    def spike(options: GrayscaleTextureOptions = DEFAULT_GRAYSCALE_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_grayscale_texture_to_pixels("./assets/objects/spike.png", **options)
    
    def orb(type: Literal["yellow", "purple", "blue", "green", "red", "black"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/orbs/orb_{type}.png", **options)
    
    def pad(type: Literal["yellow", "purple", "blue", "red"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_colorful_texture_to_pixels(f"./assets/objects/pads/pad_{type}.png", **options)

    def get_transformed_texture(self, level_obj: "Level", object: "LevelObject") -> np.ndarray:
        """
        Given a `LevelObject`, attempts to search & return its specific texture in the cache.
        If not found, calculates the transformed texture of the object,
        with the correct rotation, reflection, and color (based on the object's color channel
        and what that color channel is currently set to in the `Level` object.
        
        Saves to texture cache. Returns the texture.
        """
        pass # TODO
    
    

# preload all textures

# load objects
TextureManager.textures.update({
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
TextureManager.textures.update({
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