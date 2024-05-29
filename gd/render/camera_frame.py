from typing import TYPE_CHECKING, Literal
from render.utils import fcode_opt as fco, blend_rgba_img_onto_rgb_img, first_diff_color, last_diff_color, lesser, greater
from draw_utils import Position, convert_to_chars as convert_to_px, print2
from time import perf_counter
from logger import Logger
import numpy as np
from render.font import Font

if TYPE_CHECKING:
    from blessed import Terminal

class CameraFrame:
    """
    Wrapper over a 2D array of pixels for rendering to the screen.
    
    Images with transparency can be added to a CameraFrame, however the final compiled result that gets
    printed to the screen will assume all alpha values are 255 (opaque).
    """

    def __init__(self, term: "Terminal"):
        self.term = term
        self.width = term.width
        """ Width in pixels = terminal width """
        self.height = term.height*2
        """ Height in pixels (2 * terminal height since each character is 2 pixels tall) """
        
        #self.chars: List[str] = []
        #""" array of strings. Each string is a row on the screen. """
        
        self.pixels: np.ndarray = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        """ 2d array of pixels. Each pixel is an rgb tuple. """

    def render_raw(self) -> None:
        """ Simply prints the frame to the screen, without the need for a previous frame. 
        Keep in mind, this is quite slow and should only be used for rendering the first frame. """

        for i in range(0, self.height, 2):
            string = ""
            for j in range(self.width):
                string += fco(self.pixels[i,j], self.pixels[i+1,j]) + '▀'
                
            print2(self.term.move_xy(0, i//2), string)

    def render(self, prev_frame: "CameraFrame") -> None:
        """ Prints the frame to the screen.
        Optimized by only printing the changes from the previous frame. """
        
        indices_to_print = []
        """ Should end up being a list of tuples (start, end) 
        where start and end are the first and last changed "pixels columns" (characters) in a row. """
        
        # compare the curr frame with the previous frame
        # for each pair of rows, find the first and last changed column
        # multiply term height by 2 since chars are 2 pixels tall
        for top_row_index in range(0, self.term.height*2, 2):            
            first_diff_row1 = first_diff_color(self.pixels[top_row_index], prev_frame.pixels[top_row_index])
            first_diff_row2 = first_diff_color(self.pixels[top_row_index+1], prev_frame.pixels[top_row_index+1])
            
            last_diff_row1 = last_diff_color(self.pixels[top_row_index], prev_frame.pixels[top_row_index])
            last_diff_row2 = last_diff_color(self.pixels[top_row_index+1], prev_frame.pixels[top_row_index+1])
            
            print_start = lesser(first_diff_row1, first_diff_row2)
            print_end = greater(last_diff_row1, last_diff_row2)
            
            indices_to_print.append((print_start, print_end))
            
        # printing the frame
        # for each pair of rows, convert the pixels from start to end into colored characters, then print.
        #Logger.log(f"[CameraFrame/render]: len of indices to print: {len(indices_to_print)}")
        start_time = perf_counter()
        total_printing_time = 0
        last_printing_time = 0
        for i in range(len(indices_to_print)-1):
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
            last_printing_time = perf_counter()
            with self.term.hidden_cursor():
                #Logger.log(f"[CameraFrame/render]: printing row {i} from {start} to {end}")
                
                print2(self.term.move_xy(int(start), int(i)), string)
            total_printing_time += perf_counter() - last_printing_time
        #Logger.log(f"[CameraFrame/render]: took {perf_counter()-start_time} seconds to draw frame, {total_printing_time} seconds to print")

    def fill(self, color: tuple) -> None:
        """ Fills the entire canvas with the given color. RGB (3-tuple) required. Should be pretty efficient because of numpy. """
        assert len(color) == 3, f"[FrameLayer/fill]: color must be an rgb (3 ints) tuple, instead got {color}"

        self.pixels[:,:] = color

    # IMPORTANT: dropped support for now, will fix later (hopefully)
    def add_rect(self, color: tuple, position: Position.Relative, width: int | str | None = None, height: int | str | None = None) -> None:
        """
        Places a rectangle on the frame with the given color and position.
        
        `color` - rgba tuple

        ### Positioning
        
        Important: If two controlling values are provided in `position`, such as `top` and `bottom`, the `height` parameter will be ignored.
        Basically, height and width params are only used if `position` only specifies one of the two dimensions, such as if `bottom` is None.
        
        If none of a dimension's controlling values are provided (`top` and `bottom` must not both be None, for example), an error will be thrown.
        """
        
        # TODO - implement outlining (shouldnt be that hard with numpy)

        conv_width = convert_to_px(self.width, width) if width is not None else self.width
        conv_height = convert_to_px(self.height, height) if height is not None else self.height
        
        abs_pos = position.get_absolute(self.width, self.height)
        
        # assert that at least one of the two dimensions is specified
        if position.top is None and position.bottom is None:
            raise ValueError("[Framelayer/add_rect] At least one of top or bottom must be specified in position.")
        
        if position.left is None and position.right is None:
            raise ValueError("[Framelayer/add_rect] At least one of left or right must be specified in position.")
        
        # find true top and left values
        true_top = abs_pos.top if abs_pos.top is not None else self.height - abs_pos.bottom - conv_height
        true_left = abs_pos.left if abs_pos.left is not None else self.width - abs_pos.right - conv_width
        
        # find true width and height
        true_width = self.width - abs_pos.right - abs_pos.left if (abs_pos.left is not None and abs_pos.right is not None) else conv_width
        true_height = self.height - abs_pos.bottom - abs_pos.top if (abs_pos.top is not None and abs_pos.bottom is not None) else conv_height
        
        Logger.log(f"FrameLayer/draw_rect position: {position}")
        
        # add rect onto the layer
        if len(color) == 3: # make everything rgba. if no a specified, assume fully opaque
            color = (*color, 255)
        self.pixels[true_top:true_top+true_height, true_left:true_left+true_width] = color

    # IMPORTANT: dropped support for now, will fix later (hopefully)
    def add_pixels(self, x: int, y: int, pixels: np.ndarray, anchor: Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"] = "top-left") -> None:
        """ 
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
        
    def add_text(self, x: int, y: int, font: Font, text: str, anchor: Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"] = "top-left") -> None:
        ...
        
    def add_text_centered(self, x: int, y: int, font: Font, text: str) -> None:
        """       
        Draws a font to the pixel array at the specified x and y values, where (x,y) are the center of the text to be rendered.
        x and y should be relative to the top left corner of the frame.
        
        Note: Fonts SHOULD be monospaced.
        """
        
        concat_pixels = np.empty((font.font_height, len(text)*font.font_width, 4), dtype=np.uint8)
        
        for i in range(len(text)):
            pixels = font.get(text[i])
            if pixels is None: raise ValueError(f"[FrameLayer/add_text_centered]: Can't render unsupported character '{text[i]}' for font @ {font.fp}")

            concat_pixels[:,i*font.font_width:(i+1)*font.font_width] = pixels
            
        # find the top left corner where the text should be placed
        left = x - concat_pixels.shape[1] // 2
        top = y - concat_pixels.shape[0] // 2
        
        # clip to 0, 0
        clipped_left = max(0, left)
        clipped_top = max(0, top)
        
        # these should always be nonnegative
        offset_top = clipped_top - top
        offset_left = clipped_left - left
        
        # if completely offscreen, return
        if offset_top >= concat_pixels.shape[0] or offset_left >= concat_pixels.shape[1]:
            return
        
        Logger.log(f"[CameraFrame/add_text_centered]: adding text at {x}, {y}, size {concat_pixels.shape}, left={left}, top={top}, clipped_left={clipped_left}, clipped_top={clipped_top}, offset_left={offset_left}, offset_top={offset_top}")
        
        # add text onto the layer, clipping if necessary
        self.pixels[clipped_top:clipped_top+concat_pixels.shape[0]-offset_top, clipped_left:clipped_left+concat_pixels.shape[1]-offset_left] =\
            blend_rgba_img_onto_rgb_img(self.pixels[
                clipped_top:clipped_top+concat_pixels.shape[0]-offset_top,
                clipped_left:clipped_left+concat_pixels.shape[1]-offset_left
                ], concat_pixels[offset_top:, offset_left:])
        #self.pixels[
        #    top:top+concat_pixels.shape[0], 
        #    left:left+concat_pixels.shape[1]
        #] = blend_rgba_img_onto_rgb_img(
        #    self.pixels[
        #        top:top+concat_pixels.shape[0],
        #        left:left+concat_pixels.shape[1]
        #    ], concat_pixels)
            
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
        
        # blend new pixels onto the layer
        self.pixels[int(clipped_y1):int(clipped_y1+pixels.shape[0]-offset_y1), int(clipped_x1):int(clipped_x1+pixels.shape[1]-offset_x1)] =\
            blend_rgba_img_onto_rgb_img(self.pixels[
                int(clipped_y1):int(clipped_y1+pixels.shape[0]-offset_y1),
                int(clipped_x1):int(clipped_x1+pixels.shape[1]-offset_x1)
                ], pixels[int(offset_y1):self.height, int(offset_x1):self.width])
        