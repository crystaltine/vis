from typing import TYPE_CHECKING, Literal, Tuple
from render.utils import fcode_opt as fco, blend_rgba_img_onto_rgb_img_inplace, first_diff_color, last_diff_color, lesser, greater, remove_ansi
from draw_utils import Position, convert_to_chars as convert_to_px, print2
from time import perf_counter
from threading import Thread
from logger import Logger
import numpy as np
from render.font import Font
from render.constants import CameraConstants

if TYPE_CHECKING:
    from blessed import Terminal

class CameraFrame:
    """
    Wrapper over a 2D array of pixels for rendering to the screen.
    
    Images with transparency can be added to a CameraFrame, however the final compiled result that gets
    printed to the screen will assume all alpha values are 255 (opaque).
    """

    def __init__(self, term: "Terminal", size: Tuple[int | None, int | None] = (None, None), pos: Tuple[int | None, int | None] = (0, 0)) -> None:
        """ Optional params:
        - `size`: tuple (width, height) in pixels. None values will default to the terminal's width/height.
        - `pos`: tuple (x, y) in pixels, where the top left corner of the frame will be placed. Defaults to (0, 0) (top left of screen)
        
        NOTE: Height and y-position MUST both be even. Each character is 2 pixels tall, and we cant render half-characters.
        """
        
        assert size[1] is None or size[1] % 2 == 0, f"[CameraFrame/__init__]: height must be even, instead got {size[1]}"
        assert pos[1] is None or pos[1] % 2 == 0, f"[CameraFrame/__init__]: y position must be even, instead got {pos[1]}"
        
        self.term = term
        self.width = size[0] if size[0] is not None else term.width
        """ Width in pixels (1px = width of 1 monospaced character) """
        self.height = size[1] if size[1] is not None else term.height*2
        """ Height in pixels (2px = height of 1 monospaced character) """
        
        self.pos = pos
        
        #self.chars: List[str] = []
        #""" array of strings. Each string is a row on the screen. """
        
        self.pixels: np.ndarray = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        """ 2d array of pixels. Each pixel is an rgb tuple. (0, 0) is the top left of the frame, not the top left of the screen. """

    def render_raw(self) -> None:
        """ Simply prints the frame to the screen, without the need for a previous frame. 
        Keep in mind, this is quite slow and should only be used for rendering the first frame. """
        
        # handle odd starting y. NOTE - this wont happen for now, since we are requiring even starting y and height.
        if self.pos[1] % 2 == 1:
            # first line prints bottom half char (top half will be terminal default bg)
            string1 = ""
            for j in range(self.width):
                string1 += fco(self.pixels[self.pos[1],j], None) + '▀'
            print2(self.term.move_xy(self.pos[0], self.pos[1]//2) + string1)
            
            # print middle rows
            stop_at = (self.pos[1] + self.height - (self.pos[1] + self.height) % 2) - 1
            # if height is even there will be an extra line at the end
            # if odd, then we just go until the end right here, since there is no last isolated line
            for i in range(self.pos[1]+1, stop_at):
                string = ""
                for j in range(self.width):
                    string += fco(self.pixels[i,j], self.pixels[i+1,j]) + '▀'
                print2(self.term.move_xy(self.pos[0], i//2) + string)
                
            # print last line if needed
            if self.height % 2 == 0: # since y is odd, if height is even, then we have another case of a single line
                string2 = ""
                for j in range(self.width):
                    string2 += fco(None, self.pixels[self.pos[1]+self.height-1,j]) + '▀'
                print2(self.term.move_xy(self.pos[0], (self.pos[1]+self.height)//2 + 1) + string2)
            
        else:
            
            #compiled_str = "" # try printing the whole thing at once
            
            for i in range(0, self.height, 2):
                string = ""
                for j in range(self.width):
                    string += fco(self.pixels[i,j], self.pixels[i+1,j]) + '▀' # for quick copy: ▀
                
                #compiled_str += string + "\n"
                print2(self.term.move_xy(self.pos[0], (i+self.pos[1])//2) + string)
            #print2(self.term.move_xy(self.pos[0], self.pos[1]//2) + compiled_str)

    def render(self, prev_frame: "CameraFrame") -> None:
        """ Prints the frame to the screen.
        Optimized by only printing the changes from the previous frame. """
        
        indices_to_print = []
        """ Should end up being a list of tuples (start, end) 
        where start and end are the first and last changed "pixels columns" (characters) in a row. """
        
        # compare the curr frame with the previous frame
        # for each pair of rows, find the first and last changed column
        # multiply term height by 2 since chars are 2 pixels tall
        for top_row_index in range(0, self.height, 2):       
            first_diff_row1 = first_diff_color(self.pixels[top_row_index], prev_frame.pixels[top_row_index])
            first_diff_row2 = first_diff_color(self.pixels[top_row_index+1], prev_frame.pixels[top_row_index+1])
            
            last_diff_row1 = last_diff_color(self.pixels[top_row_index], prev_frame.pixels[top_row_index])
            last_diff_row2 = last_diff_color(self.pixels[top_row_index+1], prev_frame.pixels[top_row_index+1])
            
            print_start = lesser(first_diff_row1, first_diff_row2)
            print_end = greater(last_diff_row1, last_diff_row2)
            
            #Logger.log(f"[CameraFrame/render]: Appending ({print_start}, {print_end}) to indices_to_print, which currently has {len(indices_to_print)} elements (b4 adding)")
            indices_to_print.append((print_start, print_end))
            
        # printing the frame
        # for each pair of rows, convert the pixels from start to end into colored characters, then print.
        for i in range(len(indices_to_print)):
            #Logger.log(f"[CameraFrame/render]: row {i} indices to print: {indices_to_print[i]}")
            start, end = indices_to_print[i]
            
            # if both are None, that means the rows were the exact same, so we don't need to print anything
            if start is None and end is None:
                #Logger.log(f"Skipping row {i} since it's the same as the previous row!")
                continue
            
            # converting the two pixel rows into a string
            string = ""
            for j in range(start, end+1):
                string += fco(self.pixels[i*2,j], self.pixels[i*2+1,j]) + '▀' # pixels1 is top, so it gets fg color. pixels2 is bottom, so it gets bg color.
            
            # go to coordinates in terminal, and print the string
            # terminal coordinates: start, i
            
            #Logger.log_on_screen(self.term, f"[CameraFrame/render]: printing@{int(start) + self.pos[0]}, {i + self.pos[1]//2} for len {end-start+1}")
            #Logger.log_on_screen(self.term, f"[CameraFrame/render]: printing@{int(start) + self.pos[0]},{i + self.pos[1]//2}: \x1b[0m[{string}\x1b[0m]")
            print2(self.term.move_xy(int(start)+self.pos[0], i+self.pos[1]//2) + string)

    def fill(self, color: tuple) -> None:
        """ Fills the entire canvas with the given color. RGB (3-tuple) required. Should be pretty efficient because of numpy. """
        assert len(color) == 3, f"[FrameLayer/fill]: color must be an rgb (3 ints) tuple, instead got {color}"

        self.pixels[:,:] = color

    def add_rect(
        self, 
        color: CameraConstants.RGBTuple | CameraConstants.RGBATuple, 
        x: int, y: int, 
        width: int, height: int,
        outline_width: int = 0,
        outline_color: CameraConstants.RGBTuple | CameraConstants.RGBATuple = (0,0,0,0),
        anchor: Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"] = "top-left",
        ) -> None:
        """ Places a rectangle on the frame with the given RGBA color and position.
        Optionally, can add an outline to the rectangle with the given width and color. 
        Can also specify what part of the rectangle x and y refer to. (default is top left)"""

        # add alpha to color if it's an rgb tuple
        if len(color) == 3:
            color = (*color, 255)
            
        rect_as_pixels = np.full((height+outline_width*2, width+outline_width*2, 4), outline_color, dtype=np.uint8)
        
        # set the middle of rect_as_pixels to the color
        rect_as_pixels[outline_width:outline_width+height, outline_width:outline_width+width] = color
        
        y1 = y - outline_width
        y2 = y + height + outline_width
        x1 = x - outline_width
        x2 = x + width + outline_width
        
        match(anchor):
            case "top-right":
                x1 -= width
                x2 -= width
            case "bottom-left":
                y1 -= height
                y2 -= height
            case "bottom-right":
                x1 -= width
                x2 -= width
                y1 -= height
                y2 -= height
            case "center":
                x1 -= width // 2
                x2 -= width // 2
                y1 -= height // 2
                y2 -= height // 2
        
        blend_rgba_img_onto_rgb_img_inplace(self.pixels[y1:y2, x1:x2], rect_as_pixels)
    
    # IMPORTANT: dropped support for now, will fix later (hopefully)
    def add_pixels(self, x: int, y: int, pixels: np.ndarray, anchor: Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"] = "top-left") -> None:
        """ 
        CURRENTLY UNSUPPORTED, PROBABLY DOESNT WORK
        
        Adds a set of pixels to the frame, with the top left corner at the given position.
        If the pixels go off the edge of the frame, they will be clipped.
        """
        left = x
        top = y
        
        # TODO - handle overflow
        
        match(anchor):
            case "top-right":
                left -= pixels.shape[1]
            case "bottom-left":
                top -= pixels.shape[0]
            case "bottom-right":
                left -= pixels.shape[1]
                top -= pixels.shape[0]
            case "center":
                left -= pixels.shape[1] // 2
                top -= pixels.shape[0] // 2
                
        self.pixels[top:top+pixels.shape[0], left:left+pixels.shape[1]] = pixels
        
    def add_text(
        self, 
        x: int, y: int, 
        font: Font, 
        text: str, 
        anchor: Literal["left", "right", "center"] = "center",
        color: CameraConstants.RGBTuple | CameraConstants.RGBATuple = (255,255,255)) -> None:
        """       
        Draws a font to the pixel array at the specified x and y values, where y is the vertical center of the text,
        and x can be specified to correspond to either the left, center, or right edges of the text.
        
        x and y should be relative to the top left corner of the frame.
        
        Note: Fonts SHOULD be monospaced.
        """
        
        pixels = font.assemble(text, color)
            
        # find the top left corner where the text should be placed
        left = ...
        top = y - pixels.shape[0] // 2
        
        # match to anchor
        match(anchor):
            case "right":
                left = x - pixels.shape[1]
            case "center":
                left = x - pixels.shape[1] // 2
            case "left":
                left = x
        
        # clip to 0, 0
        clipped_left = max(0, left)
        clipped_top = max(0, top)
        
        # these should always be nonnegative
        offset_top = clipped_top - top
        offset_left = clipped_left - left
        
        # if completely offscreen, return
        #if offset_top >= pixels.shape[0] or offset_left >= pixels.shape[1]:
        #    return

        blend_rgba_img_onto_rgb_img_inplace(
            self.pixels[clipped_top:clipped_top+pixels.shape[0]-offset_top, clipped_left:clipped_left+pixels.shape[1]-offset_left],
            pixels[offset_top:, offset_left:]
        )

    def add_pixels_topleft(self, x: int, y: int, pixels: np.ndarray) -> None:
        """ Same as add_pixels, but with the anchor set to top-left. mainly for optimization. """
        #Logger.log(f"[FrameLayer/add_pixels_topleft]: adding pixels at {x}, {y}, size {pixels.shape}")

        # if x or y are negative, clip them
        clipped_y1 = max(0, y)
        #clipped_y2 = min(self.height, y+pixels.shape[0])
        clipped_x1 = max(0, x)
        #clipped_x2 = min(self.width, x+pixels.shape[1])
        
        # these should always be nonnegative
        offset_x1 = clipped_x1 - x
        #offset_x2 = clipped_x2 - x
        offset_y1 = clipped_y1 - y
        #offset_y2 = clipped_y2 - y
        
        # TODO - this shouldnt happen, but we catch just in case
        if offset_x1 >= pixels.shape[1] or offset_y1 >= pixels.shape[0]:
            #Logger.log(f"[FrameLayer/add_pixels_topleft]: clipped off all pixels, returning")
            return

        blend_rgba_img_onto_rgb_img_inplace(
            self.pixels[int(clipped_y1):int(clipped_y1+pixels.shape[0]-offset_y1), int(clipped_x1):int(clipped_x1+pixels.shape[1]-offset_x1)],
            pixels[int(offset_y1):self.height, int(offset_x1):self.width]
        )
    
    def add_pixels_centered_at(self, x: int, y: int, pixels: np.ndarray) -> None:
        """ Adds a set of pixels to the frame, with the center at the given position. """
        # find the range that would actually be visible
        # find true topleft
        
        pixels_height_1 = pixels.shape[0] // 2
        pixels_height_2 = pixels.shape[0] - pixels_height_1
        pixels_width_1 = pixels.shape[1] // 2
        pixels_width_2 = pixels.shape[1] - pixels_width_1
        
        left = x - pixels_width_1
        top = y - pixels_height_1
        
        clipped_left = int(max(0, left))
        clipped_top = int(max(0, top))
        
        offset_left = int(clipped_left - left)
        offset_top = int(clipped_top - top)
        
        # ignore if fully offscreen
        #if offset_left >= pixels_width_2 or offset_top >= pixels_height_2:
        #    return
        
        #Logger.log(f"[CameraFrame/add_pixels_centered_at]: adding pixels at {x}, {y}, size {pixels.shape}, left={left}, top={top}, clipped_left={clipped_left}, clipped_top={clipped_top}, offset_left={offset_left}, offset_top={offset_top}")
        #Logger.log(f"^^^ Final indices to use: self.pixels[{clipped_top}:{clipped_top+pixels.shape[0]-offset_top}, {clipped_left}:{clipped_left+pixels.shape[1]-offset_left}]")
        #Logger.log(f"^^^ Indices for pixels: pixels[{offset_top}:{pixels.shape[0]}, {offset_left}:{pixels.shape[1]}]")
        
        if clipped_top+pixels.shape[0]-offset_top <= 0: # if the top is offscreen
            return
        
        if clipped_left+pixels.shape[1]-offset_left <= 0: # if the left is offscreen
            return
        
        #Logger.log(f"indices for self.pixels: self.pixels[{clipped_top}:{clipped_top+pixels.shape[0]-offset_top}, {clipped_left}:{clipped_left+pixels.shape[1]-offset_left}]")
        
        blend_rgba_img_onto_rgb_img_inplace(
            self.pixels[clipped_top:int(clipped_top+pixels.shape[0]-offset_top), clipped_left:int(clipped_left+pixels.shape[1]-offset_left)],
            pixels[offset_top:, offset_left:]
        )
        
    def copy(self) -> "CameraFrame":
        """ Returns a deep copy of this CameraFrame. (except for the terminal reference) """
        new_frame = CameraFrame(self.term, (self.width, self.height), self.pos)
        new_frame.pixels = np.copy(self.pixels)
        return new_frame