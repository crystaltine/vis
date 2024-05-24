from typing import Dict, List, TYPE_CHECKING, Literal
from render.utils import fcode_opt as fco, blend_pixels, blend_multiple_pixels, first_diff_color, last_diff_color, lesser, greater
from draw_utils import Position, convert_to_chars as convert_to_px, print2
from time import perf_counter
from logger import Logger
import numpy as np

vec_blend_multiple_pixels = np.vectorize(blend_multiple_pixels)

if TYPE_CHECKING:
    from blessed import Terminal

class CameraFrame:
    """
    Wrapper over a set of 2d arrays (represented by FrameLayer objs) that stores a frame to be rendered to the screen.

    Supports layers. 
    """

    def __init__(self, term: "Terminal"):
        self.term = term
        self.width = term.width
        self.height = term.height*2
        """ In pixels, so will be 2x the terminal height. """

        self.layers: Dict[str, FrameLayer] = {}
        """ Dict of {Layer name : Framelayer} """
        
        self.layer_order: List[str] = []
        """ List of layer names in the order they should be rendered. i=0 is bottommost. """
        
        self.compiled: np.ndarray | None = None
        """ A compiled frame (basically all layers combined) of pixels for rendering. Is only set after .compile() is run on this instance. """
        
    def add_empty_layer(self, name: str, index: int = None) -> "FrameLayer":
        """ Creates a new layer with the given name at the given index. 0 is bottommost. 
        Pushes layers up if inserting. Adds on top if index not specified. Returns the layer. """
        self.layers[name] = FrameLayer(self.width, self.height)
        #Logger.log(f"[CameraFrame/add_empty_layer]: added a new layer with name {name}")
        self.layer_order.insert(index if index is not None else len(self.layer_order), name)
        
        return self.layers[name]
        
    def move_layer(self, name: str, new_index: int) -> None:
        """ Moves the layer with the given name to the given index. 0 is bottommost. """
        self.layer_order.remove(name)
        self.layer_order.insert(new_index, name)

    def compile(self) -> None:
        """ Combines all layers into one frame and sets it as this object's .compiled field. Assumes all layers are the same size. """
        
        compile_start_time = perf_counter()
        
        self.compiled = np.zeros((self.height, self.width, 4), dtype=np.int32)
        #Logger.log(f"[CameraFrame/compile]: time to create zeros array: {perf_counter()-compile_start_time} seconds")
        
        # doing this the slow way for now (TODO - optimize)
        for layer_name in self.layer_order:
            for y in range(self.height):
                for x in range(self.width):
                    if self.layers[layer_name].pixels[y,x][3] == 0: continue # if alpha is 0, skip
                    #if x == 0:
                    #    Logger.log(f"about to call blend_pixels with params: {self.compiled[y,x]}, {self.layers[layer_name].pixels[y,x]}")
                    self.compiled[y,x] = blend_pixels(self.compiled[y,x], self.layers[layer_name].pixels[y,x])
                    #if x == 0:
                    #    Logger.log(f"blending pixels result: {a}")
            #self.compiled = np.apply_along_axis(lambda x: blend_pixels(x[:4], x[4:]), 2, np.dstack((self.compiled, self.layers[layer_name].pixels)))

        Logger.log(f"[CameraFrame/compile]: took {perf_counter()-compile_start_time} seconds to compile frame")

    def render_raw(self, recompile=False) -> None:
        """ Simply prints the frame to the screen, without the need for a previous frame. 
        If any alphas are not 255, they are ignored. (everything is fully opaque). Also auto compiles the frame if never done so. """
        
        if self.compiled is None or recompile: self.compile()
        
        #Logger.log(f"[CameraFrame/render_raw]: compiled shape: {self.compiled.shape}")
        #Logger.log(f"[CameraFrame/render_raw]: top 10x10 for self.compiled: {self.compiled[:10,:10]}")
        
        for i in range(0, self.term.height*2-2, 2):
            string = ""
            for j in range(self.term.width):
                string += fco(self.compiled[i,j], self.compiled[i+1,j]) + '▀'
            with self.term.hidden_cursor():
                print2(self.term.move_xy(0, i//2), string)

    def render(self, prev_frame: "CameraFrame", recompile=False) -> None:
        """        
        Actually prints the frame to the screen.
        Optimized by only printing the changes from the previous frame.
    
        ### Important: will autocompile the previous frame if it has never been compiled before.
        If recompile is False (default), will not recompile this frame if it has already been compiled. if true, compiles this frame no matter what.
        
        The algorithm for this:
        First, compile the frame into just one layer.
        Then, compare the compiled frame with the previous compiled frame.
        For every row, only print the pixels from the first changed pixel to the last changed pixel.
        
        Remember that for printing, we have to do 2 rows at once since a pixel is half a character.
        """
        
        # if prev frame isn't compiled yet, do that (throw error instead?)
        if prev_frame.compiled is None: prev_frame.compile()
        
        # if curr frame isn't compiled yet, or recompile was requested, do that        
        if self.compiled is None or recompile: self.compile()
        
        # important: overlay self compiled ON TOP of prev_frame.compiled, and use that to compare for diffs
        # use slow method again
        new_pixels = np.zeros((self.height, self.width, 4), dtype=np.int32)
        for y in range(self.height):
            for x in range(self.width):
                new_pixels[y,x] = blend_pixels(prev_frame.compiled[y,x], self.compiled[y,x])
                
        #Logger.log(f"[CameraFrame/render]: top 10x10 for new stuff: {new_pixels[:10,:10]}")
        #Logger.log(f"[CameraFrame/render]: top 10x10 for prev_frame.compiled: {prev_frame.compiled[:10,:10]}")
        
        
        indices_to_print = []
        """ Should end up being a list of tuples (start, end) 
        where start and end are the first and last changed "pixels columns" (characters) in a row. """
        
        # compare the compiled frame with the previous frame
        # for each pair of rows, find the first and last changed column
        # multiply term height by 2 since chars are 2 pixels tall
        for top_row_index in range(0, self.term.height*2, 2):            
            first_diff_row1 = first_diff_color(new_pixels[top_row_index], prev_frame.compiled[top_row_index])
            first_diff_row2 = first_diff_color(new_pixels[top_row_index+1], prev_frame.compiled[top_row_index+1])
            
            last_diff_row1 = last_diff_color(new_pixels[top_row_index], prev_frame.compiled[top_row_index])
            last_diff_row2 = last_diff_color(new_pixels[top_row_index+1], prev_frame.compiled[top_row_index+1])
            
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
                string += fco(new_pixels[i*2,j], new_pixels[i*2+1,j]) + '▀' # pixels1 is top, so it gets fg color. pixels2 is bottom, so it gets bg color.
            
            # go to coordinates in terminal, and print the string
            # terminal coordinates: start, i
            last_printing_time = perf_counter()
            with self.term.hidden_cursor():
                #Logger.log(f"[CameraFrame/render]: printing row {i} from {start} to {end}")
                
                print2(self.term.move_xy(int(start), int(i)), string)
            total_printing_time += perf_counter() - last_printing_time
        Logger.log(f"[CameraFrame/render]: took {perf_counter()-start_time} seconds to draw frame, {total_printing_time} seconds to print")

class FrameLayer:
    """ A single layer of a CameraFrame. Contains a 2d array of pixels (rgba). """
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.pixels: np.ndarray = np.zeros((height, width, 4), dtype=np.int32)
        """ 2d array of pixels. Each pixel is an rgba tuple. """
        
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
    
    def fill(self, color: tuple) -> None:
        """ Fills the entire layer with the given color. RGB or RGBA tuple required. """
        if len(color) == 3: # make everything rgba. if no a specified, assume fully opaque
            color = (*color, 255)
        
        Logger.log(f"[FrameLayer/fill]: filling layer with color {color}")
        self.pixels[:,:] = color
    
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
        
    def add_pixels_topleft(self, x: int, y: int, pixels: np.ndarray) -> None:
        """ same as add_pixels, but with the anchor set to top-left. mainly for optimization. """
        #Logger.log(f"[FrameLayer/add_pixels_topleft]: adding pixels at {x}, {y}, size {pixels.shape}")
        
        # if x or y are negative, clip them
        clipped_y = max(0, y)
        clipped_x = max(0, x)
        
        clipped_off_x = clipped_x - x
        clipped_off_y = clipped_y - y
        Logger.log(f"[FrameLayer/add_pixels_topleft]: x and y are {x}, {y}, clipped to {clipped_x}, {clipped_y}")
        
        # TODO - this shouldnt happen
        if clipped_off_x >= pixels.shape[1] or clipped_off_y >= pixels.shape[0]:
            Logger.log(f"[FrameLayer/add_pixels_topleft]: clipped off all pixels, returning")
            return
        
        Logger.log(f"[FrameLayer/add_pixels_topleft] rendering this slice of pixels: [{clipped_off_y}:,{clipped_off_x}:] @ {clipped_y},{clipped_x}")
        self.pixels[clipped_y:clipped_y+pixels.shape[0]-clipped_off_y, clipped_x:clipped_x+pixels.shape[1]-clipped_off_x] = pixels[clipped_off_y:, clipped_off_x:]

# unused - use [int, int, int, int] (rgba) for numpy compatibility instead
# class Pixel:
#     """
#     Represents a single pixel in the screen, which is half of a monospaced character.
# 
#     Stores data on the color and whether or not it is the top half or bottom half of a character.
#     """
# 
#     def __init__(self, color: tuple, is_top_half: bool) -> None:
#         self.color = color
#         """ Should be a rgb(a?)255 tuple ONLY (got rid of hexcode for optimization) """
# 
#         self.is_top_half = is_top_half
# 
#     def compile_to_char(self, other: "Pixel") -> str:
#         """
#         Combines this pixel with another to create a colored character (block element)
#         with ANSI color codes. Make sure other is the other half of the character (both cant be the same half)
#         
#         For optimization, the string this function returns does not have a format reset code at the end,
#         meaning all formatting will carry to the next char unless it specifies otherwise (which it should)
#         """
#         if self.is_top_half == other.is_top_half:
#             raise ValueError(f"[Pixel/compile_to_char] Cannot compile pixels that both have is_top_half={self.is_top_half}")
# 
#         color_code = fco(fg=self.color,bg=other.color) if self.is_top_half else fco(fg=other.color,bg=self.color)
# 
#         return color_code + "▀"