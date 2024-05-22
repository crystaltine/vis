from render.utils import fc, mix_colors
from typing import List, Literal, TypedDict
from PIL import Image
import numpy as np

# IMPORTANT TODO - textures should be able to change color and stuff. also, player icon can change.

class TextureManager:
    
    RS = "\033[0m"
    bg_color = "#287DFF"
    """ Can change throughout the level using triggers. probably best to keep it a hexcode of format `#rrggbb`. """
    ground_color = "#0046cf"
    """ Can change throughout the level using triggers. probably best to keep it a hexcode of format `#rrggbb`. """
    
    premade_textures = {}
    
    def get(texture_name: str):
        return getattr(TextureManager, texture_name)
    
    def get_raw_obj_text(texture_name: str):
        return getattr(TextureManager, "raw_" + texture_name)

    # note: for pixels, fg color = top half, bg color = bottom half
    # note2: i know this code is ugly asf but it makes it easy to update the textures later
    # note3: might upgrade to grayscale texture files in the future, and write a texture parser to apply colors/scale/rotation/reflection

    class GrayscaleTextureOptions(TypedDict):
        edge_color: str | tuple
        bg_color: str | tuple
        scale: int
        rotation: Literal["up", "right", "down", "left"]
        reflections: Literal["none", "vert", "horiz", "both"]
    class ColorfulTextureOptions(TypedDict):
        scale: int
        rotation: Literal["up", "right", "down", "left"]
        reflections: Literal["none", "vert", "horiz", "both"]
    DEFAULT_GRAYSCALE_TEXTURE_OPTIONS: GrayscaleTextureOptions = {
        "edge_color": "#ffffff",
        "bg_color": "#000000",
        "scale": 1,
        "rotation": "up",
        "reflections": "none"
    }
    DEFAULT_COLORFUL_TEXTURE_OPTIONS: ColorfulTextureOptions = {
        "scale": 1,
        "rotation": "up",
        "reflections": "none"
    }

    def build_grayscale_texture(
        filepath: str,
        edge_color: str | tuple = "#ffffff",
        bg_color: str | tuple = "#000000",
        scale: int = 1,
        rotation: Literal["up", "right", "down", "left"] = "up",
        reflections: Literal["none", "vert", "horiz", "both"] = "none",
        transparency_color: str | tuple = None) -> list[str]:
        """
        Internal function for "compiling" a texture from a grayscale image. (applies colors, scale, rotation, reflections)
        Basically turns a png file into a list of str, where each element is "▀" with some ANSI formatting applied (for color)
        
        ## New! - transparency support! Pass in transparency_color as a hexcode (preferably) to render alpha on top of it.
        If `transparency_color` is None, the current bg color (`TextureManager.bg_color`) will be used.
        """
        
        im = Image.open(filepath)
        transparency_color = TextureManager.bg_color if transparency_color is None else transparency_color
        
        # apply scaling if necessary
        if scale != 1:
            if not isinstance(scale, int): raise ValueError("[render texture grayscale]: scale must be an integer")
            im = im.resize((im.width * scale, im.height * scale))

        pixels = np.array(im, dtype=np.uint8)
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
                
                top_px_midtone = mix_colors(transparency_color, mix_colors(edge_color, bg_color, top_px_gray), top_px_alpha)
                bottom_px_midtone = mix_colors(transparency_color, mix_colors(edge_color, bg_color, bottom_px_gray), bottom_px_alpha)
                
                final_row.append(f"\x1b[0m{fc(fg=top_px_midtone, bg=bottom_px_midtone)}▀")
                
            final_chars.append(final_row)
        
        final_chars = np.array(final_chars)
        
        # apply any changes
        rotation_values = {"up": 0, "right": 3, "down": 2, "left": 1}
        final_chars = np.rot90(final_chars, rotation_values[rotation])
        
        if reflections == "vert":
            final_chars = np.flipud(final_chars)
        elif reflections == "horiz":
            final_chars = np.fliplr(final_chars)
        elif reflections == "both":
            final_chars = np.flipud(np.fliplr(final_chars))
            
        return ["".join(row) for row in final_chars]

    def build_colorful_texture(
        filepath: str,
        scale: int = 1,
        rotation: Literal["up", "right", "down", "left"] = "up",
        reflections: Literal["none", "vert", "horiz", "both"] = "none",
        transparency_color: str | tuple = None) -> list[str]:
        """
        Internal function for "compiling" a texture from a colorful image. (applies scale, rotation, reflections)
        The same as build_grayscale_texture, but does not take in edge_color and bg_color, and instead uses the colors from the image.
        Basically turns a png file into a list of str, where each element is "▀" with some ANSI formatting applied (for color)
        
        ## New! - transparency support! Pass in transparency_color as a hexcode (preferably) to render alpha on top of it.
        If `transparency_color` is None, the current bg color (`TextureManager.bg_color`) will be used.
        """
        
        im = Image.open(filepath)
        transparency_color = TextureManager.bg_color if transparency_color is None else transparency_color
        
        # apply scaling if necessary
        if scale != 1:
            if not isinstance(scale, int): raise ValueError("[render texture colorful]: scale must be an integer")
            im = im.resize((im.width * scale, im.height * scale))

        pixels = np.array(im, dtype=np.uint8)
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
        rotation_values = {"up": 0, "right": 3, "down": 2, "left": 1}
        final_chars = np.rot90(final_chars, rotation_values[rotation])
        
        if reflections == "vert":
            final_chars = np.flipud(final_chars)
        elif reflections == "horiz":
            final_chars = np.fliplr(final_chars)
        elif reflections == "both":
            final_chars = np.flipud(np.fliplr(final_chars))
            
        return ["".join(row) for row in final_chars]

    def spike(options: GrayscaleTextureOptions = DEFAULT_GRAYSCALE_TEXTURE_OPTIONS) -> list[str]:
        return TextureManager.build_grayscale_texture("textures/spike.png", **options)
    
    def orb(type: Literal["yellow", "purple", "blue", "green", "red", "black"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> list[str]:
        return TextureManager.build_colorful_texture(f"../assets/textures/orb_{type}.png", **options)
    premade_textures.update(premade_orb_types := {
        "yellow_orb": orb("yellow"),
        "purple_orb": orb("purple"),
        "blue_orb": orb("blue"),
        "green_orb": orb("green"),
        "red_orb": orb("red"),
        "black_orb": orb("black")
    })
    
    def pad(type: Literal["yellow", "purple", "blue", "red"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> list[str]:
        return TextureManager.build_colorful_texture(f"../assets/textures/pad_{type}.png", **options)
    premade_textures.update(premade_pad_types := {
        "yellow_pad": pad("yellow"),
        "purple_pad": pad("purple"),
        "blue_pad": pad("blue"),
        "red_pad": pad("red")
    })
    
    def mode_portal(type: Literal["cube", "ship", "ball", "ufo", "wave", "robot", "spider"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> list[str]:
        return TextureManager.build_colorful_texture(f"../assets/textures/mode_portal_{type}.png", **options)
    premade_textures.update(premade_mode_portal_types := {
        "cube_portal": mode_portal("cube"),
        "ship_portal": mode_portal("ship"),
        "ball_portal": mode_portal("ball"),
        "ufo_portal": mode_portal("ufo"),
        "wave_portal": mode_portal("wave"),
        "robot_portal": mode_portal("robot"),
        "spider_portal": mode_portal("spider")
    })
    
    def grav_portal(type: Literal["normal", "reverse"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> list[str]:
        return TextureManager.build_colorful_texture(f"../assets/textures/grav_portal_{type}.png", **options)
    premade_textures.update(premade_grav_portal_types := {
        "normal_grav_portal": grav_portal("normal"),
        "reverse_grav_portal": grav_portal("reverse")
    })
    
    def speed_portal(type: Literal["half", "normal", "double", "triple"], options: ColorfulTextureOptions = DEFAULT_COLORFUL_TEXTURE_OPTIONS) -> list[str]:
        return TextureManager.build_colorful_texture(f"../assets/textures/speed_portal_{type}.png", **options)
    premade_textures.update(premade_speed_portal_types := {
        "half_speed_portal": speed_portal("half"),
        "normal_speed_portal": speed_portal("normal"),
        "double_speed_portal": speed_portal("double"),
        "triple_speed_portal": speed_portal("triple")
    })
    
    def block0(index: int, options: GrayscaleTextureOptions = DEFAULT_GRAYSCALE_TEXTURE_OPTIONS) -> list[str]:
        """
        Indices - determines which edges are filled in. (for connected texture support)
        e.g. 0 is all edges filled, 1 is 3 edges filled, etc.
        """
        return TextureManager.build_grayscale_texture(f"textures/block0_{index}.png", **options)