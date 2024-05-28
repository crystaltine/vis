from render.utils import fc, mix_colors, mix_colors_opt as mco
from typing import List, Literal, TypedDict
from logger import Logger
from PIL import Image
import numpy as np
import traceback

# IMPORTANT TODO - textures should be able to change color and stuff. also, player icon can change.

ROTATION_VALUES = {"up": 0, "right": 3, "down": 2, "left": 1}

class GrayscaleTextureOptions(TypedDict):
    replace_dark_with: str | tuple
    replace_light_with: str | tuple
    scale: int
    rotation: Literal["up", "right", "down", "left"]
    reflections: Literal["none", "vert", "horiz", "both"]
    
class ColorfulTextureOptions(TypedDict):
    scale: int
    rotation: Literal["up", "right", "down", "left"]
    reflections: Literal["none", "vert", "horiz", "both"]

class TextureManager:
    
    RS = "\033[0m"
    bg_color: tuple = (24, 67, 240)
    """ Can change throughout the level using triggers. keep as rgb tuple. """
    ground_color: tuple = (8, 32, 170)
    """ Can change throughout the level using triggers. keep as rgb tuple. """
    
    curr_player_icon: np.ndarray = ... # set lower down
    
    premade_textures = {}
    
    def get(texture_name: str):
        return TextureManager.premade_textures[texture_name]
    
    def get_raw_obj_text(texture_name: str):
        return getattr(TextureManager, "raw_" + texture_name)

    DEFAULT_GRAYSCALE_TEXTURE_OPTIONS: GrayscaleTextureOptions = {
        "replace_dark_with": (0, 0, 0),
        "replace_light_with": (255, 255, 255),
        "scale": 1,
        "rotation": "up",
        "reflections": "none"
    }
    DEFAULT_COLORFUL_TEXTURE_OPTIONS: ColorfulTextureOptions = {
        "scale": 1,
        "rotation": "up",
        "reflections": "none"
    }

    # should be unused due to new rendering system not needing chars
    @staticmethod
    def build_grayscale_texture(
        filepath: str,
        replace_dark_with: str | tuple = "#000000",
        replace_light_with: str | tuple = "#ffffff",
        scale: int = 1,
        rotation: Literal["up", "right", "down", "left"] = "up",
        reflections: Literal["none", "vert", "horiz", "both"] = "none",
        transparency_color: str | tuple = None) -> list[str]:
        """
        Internal function for "compiling" a texture from a grayscale image. (applies colors, scale, rotation, reflections)
        Basically turns a png file into a list of str, where each element is "▀" with some ANSI formatting applied (for color)
        
        ## New! - transparency support! Pass in transparency_color as a hexcode (preferably) to render alpha on top of it.
        If `transparency_color` is None, the current bg color (`TextureManager.replace_light_with`) will be used.
        """
        
        im = Image.open(filepath)
        transparency_color = TextureManager.replace_light_with if transparency_color is None else transparency_color
        
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
        
        if reflections == "vert":
            final_chars = np.flipud(final_chars)
        elif reflections == "horiz":
            final_chars = np.fliplr(final_chars)
        elif reflections == "both":
            final_chars = np.flipud(np.fliplr(final_chars))
            
        return ["".join(row) for row in final_chars]
    
    @staticmethod
    def build_grayscale_texture_to_pixels(
        filepath: str,
        replace_dark_with: tuple = (0, 0, 0),
        replace_light_with: tuple = (255, 255, 255),
        scale: int = 1,
        rotation: Literal["up", "right", "down", "left"] = "up",
        reflections: Literal["none", "vert", "horiz", "both"] = "none"
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
        
        if reflections == "vert":
            final_pixels = np.flipud(final_pixels)
        elif reflections == "horiz":
            final_pixels = np.fliplr(final_pixels)
        elif reflections == "both":
            final_pixels = np.flipud(np.fliplr(final_pixels))
            
        return final_pixels

    # should be unused due to new rendering system not needing chars
    @staticmethod
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
        
        if reflections == "vert":
            final_chars = np.flipud(final_chars)
        elif reflections == "horiz":
            final_chars = np.fliplr(final_chars)
        elif reflections == "both":
            final_chars = np.flipud(np.fliplr(final_chars))
            
        return ["".join(row) for row in final_chars]

    @staticmethod
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
        
        if reflections == "vert":
            final_pixels = np.flipud(final_pixels)
        elif reflections == "horiz":
            final_pixels = np.fliplr(final_pixels)
        elif reflections == "both":
            final_pixels = np.flipud(np.fliplr(final_pixels))
        
        return final_pixels

    curr_player_icon = build_grayscale_texture_to_pixels("assets/textures/default_cube.png", (120, 202, 102), (118, 231, 241))

    def spike(options: GrayscaleTextureOptions = DEFAULT_GRAYSCALE_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_grayscale_texture_to_pixels("./assets/textures/spike.png", **options)
    
    def orb(type: Literal["yellow", "purple", "blue", "green", "red", "black"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_colorful_texture_to_pixels(f"./assets/textures/orb_{type}.png", **options)
    
    def pad(type: Literal["yellow", "purple", "blue", "red"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_colorful_texture_to_pixels(f"./assets/textures/pad_{type}.png", **options)
    
    def mode_portal(type: Literal["cube", "ship", "ball", "ufo", "wave", "robot", "spider"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_colorful_texture_to_pixels(f"./assets/textures/mode_portal_{type}.png", **options)

    def grav_portal(type: Literal["normal", "reverse"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_colorful_texture_to_pixels(f"./assets/textures/grav_portal_{type}.png", **options)

    def speed_portal(type: Literal["half", "normal", "double", "triple"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> np.ndarray:
        return TextureManager.build_colorful_texture_to_pixels(f"./assets/textures/speed_portal_{type}.png", **options)

    def block0(index: int, options: GrayscaleTextureOptions = DEFAULT_GRAYSCALE_TEXTURE_OPTIONS) -> np.ndarray:
        """
        Indices - determines which edges are filled in. (for connected texture support)
        e.g. 0 is all edges filled, 1 is 3 edges filled, etc.

        Indices go from 0 to 10. See ./assets/textures/texture_map for the block textures.
        Index starts at 0 for the highest block texture, then goes down and to the right.
        """
        return TextureManager.build_grayscale_texture_to_pixels(f"./assets/textures/block0/{index}.png", **options)
    
TextureManager.premade_textures.update({
    "spike": TextureManager.spike(),
    "yellow_orb": TextureManager.orb("yellow"),
    "purple_orb": TextureManager.orb("purple"),
    "blue_orb": TextureManager.orb("blue"),
    "green_orb": TextureManager.orb("green"),
    "red_orb": TextureManager.orb("red"),
    "black_orb": TextureManager.orb("black"),
    "yellow_pad": TextureManager.pad("yellow"),
    "purple_pad": TextureManager.pad("purple"),
    "blue_pad": TextureManager.pad("blue"),
    "red_pad": TextureManager.pad("red"),
    "cube_portal": TextureManager.mode_portal("cube"),
    "ship_portal": TextureManager.mode_portal("ship"),
    "ball_portal": TextureManager.mode_portal("ball"),
    "ufo_portal": TextureManager.mode_portal("ufo"),
    "wave_portal": TextureManager.mode_portal("wave"),
    "robot_portal": TextureManager.mode_portal("robot"),
    "spider_portal": TextureManager.mode_portal("spider"),
    "normal_grav_portal": TextureManager.grav_portal("normal"),
    "reverse_grav_portal": TextureManager.grav_portal("reverse"),
    "half_speed_portal": TextureManager.speed_portal("half"),
    "normal_speed_portal": TextureManager.speed_portal("normal"),
    "double_speed_portal": TextureManager.speed_portal("double"),
    "triple_speed_portal": TextureManager.speed_portal("triple"),
    "quadruple_speed_portal": TextureManager.speed_portal("quadruple")
})
TextureManager.premade_textures.update({
    f"block0_{i}": TextureManager.block0(i) for i in range(11)
})