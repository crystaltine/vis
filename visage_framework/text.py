from element import Element
from utils import fcode, convert_to_chars, print3
from typing import Literal, Tuple, Unpack
from globalvars import Globals
from logger import Logger
from boundary import Boundary
from time import time

class Text(Element):
    """
    Leaf-level element that renders stylable text.
    """
    
    class Attributes(Element.Attributes):
        id: str | None
        class_str: str | None
        style_str: str | None
        text: str
    
    class StyleProps(Element.StyleProps):
        """
        A typeddict of style options for text. No `top` or `bottom` because one line only.
        
        Left overrides right (if both not None, `right` is ignored). Cannot have both set to None.
        """
        position: str
        visible: bool
        color: str | tuple 
        bg_color: str | tuple
        bold: bool
        italic: bool
        underline: bool
        left: int | None
        center: int | None
        right: int | None
        top: int | None
        width: int | str | None
        height: int | None
        wrap: bool
        text_align: Literal["left", "center", "right"]
    
    SUPPORTS_CHILDREN = False
    DEFAULT_STYLE: "Text.StyleProps" = {
        "position": "relative",
        "visible": True,
        "color": "white",
        "bg_color": "transparent",
        "bold": False,
        "italic": False,
        "underline": False,
        "left": 0, # overrides right if not None
        "center": None, # overrides left and right if not None
        "right": None,
        "top": 0,
        "width": "auto", # can only be None (auto) if wrap is False, else required
        "height": None, # auto based on text length
        "wrap": False,
        "text_align": "left",
    }
    
    def __init__(self, **attrs: Unpack["Attributes"]):
        """ Keyword arguments: `Text.Attributes`:
        - id: str | None
        - class_str: str | None
        - style_str: str | None
        - text: str
        """
        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        self.text = attrs.get("text", "")

    def render(self, container_bounds: Boundary = None, container_bg: str = None) -> None:
        
        container_bounds = self.get_true_container_edges(container_bounds)
        container_width = container_bounds.right - container_bounds.left
        curr_bg_color = self.getset_curr_bg_color(container_bg)

        _w = self.style.get("width") # convenience 
        self.client_width = convert_to_chars(container_width, _w) if _w not in [None, 'auto'] else None
        if not self.style.get("wrap") and (_w is None or _w == 'auto'): # if no wrap and width is set to auto, then can auto-calc width based
            self.client_width = len(self.text)
            
        if self.client_width is None:
            Logger.log(f"Text element: incorrectly defined width (must be set if wrap is True) - style.width:{self.style.get('width')}, wrap:{self.style.get('wrap')}")
            raise ValueError("Text element: incorrectly defined width (must be set if wrap is True)")

        # to handle center: pretend left = center, and subtract half of width from it later
        true_l = convert_to_chars(container_width, self.style.get("left")) if self.style.get("left") is not None else \
            container_width - convert_to_chars(container_width, self.style.get("right")) - self.client_width
        if self.style.get("center") is not None: # this overrides left as well
            true_l = convert_to_chars(container_width, self.style.get("center")) - self.client_width//2
        
        self.client_left = container_bounds.left + true_l
        self.client_right = container_bounds.left + true_l + self.client_width       
        
        # if height is none, then dynamically calculate based on how 
        # many lines of text there are.
        # if wrap is false, then theres just one line max (0 if empty text)
        self.client_top = container_bounds.top + convert_to_chars(container_bounds.bottom - container_bounds.top, self.style.get("top"))
        if self.style.get("height") is None:
            self.client_height = (len(self.text) // self.client_width + 1) if self.style.get("wrap") else (1 if self.text else 0)              
        else: # if height is explicitly defined then, well, yeah.
            self.client_height = convert_to_chars(container_bounds.bottom-container_bounds.top, self.style.get("height"))
        self.client_bottom = self.client_top + self.client_height 

        if not self.style.get("visible"): return
            
        style_string = " ".join([
            "bold" if self.style.get("bold") else "",
            "italic" if self.style.get("italic") else "",
            "underline" if self.style.get("underline") else ""
        ])
        
        wrapped_text = [self.text]
        if self.style.get("wrap") == True:
            # wrap text based on client width
            wrapped_text = [self.text[i*self.client_width:(i+1)*self.client_width] for i in range(len(self.text)//self.client_width+1)]


        text_chunk_index = 0 # which chunk of text to render on each line
        for row in range(self.client_top, self.client_bottom):
            text_chunk = wrapped_text[text_chunk_index] if text_chunk_index < len(wrapped_text) else ""
            
            # if the text chunk is not as long as the client width, then apply text_align
            text_left_padding = 0 # 0 by default
            if len(text_chunk) < self.client_width:
                text_left_padding = (
                    (self.client_width - len(text_chunk))//2+1 if self.style.get("text_align") == "center"
                    else self.client_width - len(text_chunk) if self.style.get("text_align") == "right"
                    else 0
                )

            #Logger.log(f"[t={time()}]: about to print some random stuff from text render()")
            #print(f"{Globals.__vis_document__.term.move_xy(4, 4)}text render soon!!! text={self.text}")
            
            #Logger.log(f"<text> w/text={self.text}: align style is {self.style.get('text_align')} and text_left_padding is {text_left_padding}, {self.client_left=}")
            #with Globals.__vis_document__.term.hidden_cursor():
            print3(Globals.__vis_document__.term.move_xy(self.client_left, row) + fcode(self.style.get("color"), background=curr_bg_color, style=style_string) + text_left_padding*" " + text_chunk)
            #Logger.log(f"[t={time()}] text with text={self.text} just got drawn")
            #Logger.log_on_screen(f"just wrote {self.text}")

            text_chunk_index += 1

    def _render_partial(self, container_bounds: Boundary, max_bounds: Boundary, container_bg: str = None) -> None:
        container_bounds = self.get_true_container_edges(container_bounds)
        container_width = container_bounds.right - container_bounds.left
        curr_bg_color = self.getset_curr_bg_color(container_bg)
        
        _w = self.style.get("width") # convenience 
        self.client_width = convert_to_chars(container_width, _w) if _w not in [None, 'auto'] else None
        if not self.style.get("wrap") and (_w is None or _w == 'auto'): # if no wrap and width is set to auto, then can auto-calc width based
            self.client_width = len(self.text)
            
        if self.client_width is None:
            Logger.log(f"Text element: incorrectly defined width (must be set if wrap is True) - style.width:{self.style.get('width')}, wrap:{self.style.get('wrap')}")
            raise ValueError("Text element: incorrectly defined width (must be set if wrap is True)")

        # calculate width-related attributes 
        container_width = container_bounds.right - container_bounds.left
        true_l = convert_to_chars(container_width, self.style.get("left"))
        
        # to handle center: pretend left = center, and subtract half of width from it later
        true_l = convert_to_chars(container_width, self.style.get("left")) if self.style.get("left") is not None else \
            container_width - convert_to_chars(container_width, self.style.get("right")) - self.client_width
        if self.style.get("center") is not None: # this overrides left as well
            true_l = convert_to_chars(container_width, self.style.get("center")) - self.client_width//2
            
        self.client_left = container_bounds.left + true_l
        self.client_right = container_bounds.left + true_l + self.client_width       
        
        # if height is none, then dynamically calculate based on how 
        # many lines of text there are.
        # if wrap is false, then theres just one line max (0 if empty text)
        self.client_top = container_bounds.top + convert_to_chars(container_bounds.bottom - container_bounds.top, self.style.get("top"))
        if self.style.get("height") is None:
            self.client_height = (len(self.text) // self.client_width + 1) if self.style.get("wrap") else (1 if self.text else 0)              
        else: # if height is explicitly defined then, well, yeah.
            self.client_height = convert_to_chars(container_bounds.bottom-container_bounds.top, self.style.get("height"))
        self.client_bottom = self.client_top + self.client_height

        # Logger.log(f"[text] PARTIALRENDER: max t,b=({max_bounds.top},{max_bounds.bottom}) cli t,b=({self.client_top},{self.client_bottom})")

        if not self.style.get("visible"): return
            
        style_string = " ".join([
            "bold" if self.style.get("bold") else "",
            "italic" if self.style.get("italic") else "",
            "underline" if self.style.get("underline") else ""
        ])
        
        wrapped_text = [self.text]
        if self.style.get("wrap") == True:
            # wrap text based on client width
            wrapped_text = [self.text[i*self.client_width:(i+1)*self.client_width] for i in range(len(self.text)//self.client_width+1)]

        # if completely out of render, just skip all this goofy ah garbage
        if (
            max_bounds.left >= self.client_right or
            max_bounds.right < self.client_left or 
            max_bounds.top >= self.client_bottom or
            max_bounds.bottom < self.client_top
        ): return

        text_chunk_index = 0 # which chunk of text to render on each line
        for row in range(self.client_top, self.client_bottom+1):
            
            if max_bounds.bottom < row < max_bounds.top:
                text_chunk_index += 1
                continue

            text_chunk = wrapped_text[text_chunk_index] if text_chunk_index < len(wrapped_text) else ""
            
            # if the text chunk is not as long as the client width, then apply text_align
            text_left_padding = 0 # 0 by default
            if len(text_chunk) < self.client_width:
                text_left_padding = (
                    (self.client_width - len(text_chunk))//2 if self.style.get("text_align") == "center"
                    else self.client_width - len(text_chunk) if self.style.get("text_align") == "right"
                    else 0
                )
            
            text_to_render = text_left_padding*" " + text_chunk
            if max_bounds.left > self.client_left: # cut off left side
                text_to_render = text_to_render[max_bounds.left-self.client_left:]
            if max_bounds.right < self.client_right: # cut off right side
                text_to_render = text_to_render[:max_bounds.right-self.client_right]

            #with Globals.__vis_document__.term.hidden_cursor():
            print3(Globals.__vis_document__.term.move_xy(self.client_left, row) + fcode(self.style.get("color"), background=curr_bg_color, style=style_string) + text_left_padding*" " + text_chunk)
            text_chunk_index += 1

    def _determine_dimensions(partial_container_bounds: Boundary) -> Tuple[int, int]:
        """
        Given partial container dimensions (such as width=40px but height undefined),
        calculates what this element's width and height would be, regardless of position.
        
        This function is mainly for dealing with the fact that text elements change in 
        height based on length of text (if wrapping is on)
        """
        pass