from element import Element
from utils import fcode, convert_to_chars
from typing import Literal, Tuple, Unpack
from globalvars import Globals
from logger import Logger
from boundary import Boundary

class Text(Element):
    """
    Leaf-level element that renders stylable text.
    """
    
    class Attributes(Element.Attributes):
        id: str | None
        class_str: str | None
        style_str: str | None
        text: str
        container_bg: str
    
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
        top: int | None
        width: int | None
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
        "left": 0,
        "top": 0,
        "width": "100%",
        "height": None, # auto based on text length
        "wrap": True,
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
        self._bg_fcode = fcode(background=self.style.get("bg_color")) if self.style.get("bg_color") != "transparent" else fcode(background=attrs.get("container_bg"))
        Logger.log(f"<text> init: containerbg={attrs.get('container_bg')}, {self.style.get('bg_color')=}, {self._bg_fcode=}")
        self.text = attrs.get("text", "")

    def render(self, container_bounds: Boundary = None):

        container_bounds = self.get_true_container_edges(container_bounds)

        # calculate width-related attributes 
        container_width = container_bounds.right - container_bounds.left
        true_l = convert_to_chars(container_width, self.style.get("left"))
        true_w = convert_to_chars(container_width, self.style.get("width"))
        self.client_left = container_bounds.left + true_l
        self.client_right = container_bounds.left + true_l + true_w       
        self.client_width = self.client_right - self.client_left 
        
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

        #with Globals.__vis_document__.term.hidden_cursor():

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
            
            Logger.log(f"<text> w/text={self.text}: align style is {self.style.get('text_align')} and text_left_padding is {text_left_padding}, {self.client_left=}")
            text_bg = (self.style.get("bg_color")) if self.style.get("bg_color") != "transparent" else self.container_bg
            Logger.log(f"<text> render(): text_bg={self.style.get('bg_color')} if it isnt transparent, else using {self.container_bg=}")

            print(Globals.__vis_document__.term.move_xy(self.client_left, row) + fcode(self.style.get("color"), background=text_bg, style=style_string) + text_left_padding*" " + text_chunk, end="\x1b[0m")
            text_chunk_index += 1

    def _render_partial(self, container_bounds: Boundary, max_bounds: Boundary) -> None:
        container_bounds = self.get_true_container_edges(container_bounds)

        # calculate width-related attributes 
        container_width = container_bounds.right - container_bounds.left
        true_l = convert_to_chars(container_width, self.style.get("left"))
        true_w = convert_to_chars(container_width, self.style.get("width"))
        self.client_left = container_bounds.left + true_l
        self.client_right = container_bounds.left + true_l + true_w       
        self.client_width = self.client_right - self.client_left 
        
        # if height is none, then dynamically calculate based on how 
        # many lines of text there are.
        # if wrap is false, then theres just one line max (0 if empty text)
        self.client_top = container_bounds.top + convert_to_chars(container_bounds.bottom - container_bounds.top, self.style.get("top"))
        if self.style.get("height") is None:
            self.client_height = (len(self.text) // self.client_width + 1) if self.style.get("wrap") else (1 if self.text else 0)              
        else: # if height is explicitly defined then, well, yeah.
            self.client_height = convert_to_chars(container_bounds.bottom-container_bounds.top, self.style.get("height"))
        self.client_bottom = self.client_top + self.client_height

        Logger.log(f"[text] PARTIALRENDER: max t,b=({max_bounds.top},{max_bounds.bottom}) cli t,b=({self.client_top},{self.client_bottom})")

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

        #with Globals.__vis_document__.term.hidden_cursor():
        for i in range(max(self.client_top, max_bounds.top), min(self.client_bottom, max_bounds.bottom)):
            
                # diagram:
                #  cli_left   bounds_left              bounds_right  cli_right
                #  |          |                        |             |
                #  --------------------------------------------------- = client_width
                #             -------------------------- = max_bounds.right - max_bounds.left
            print(Globals.__vis_document__.term.move_xy(max(self.client_left, max_bounds.left), i) + self._bg_fcode + " " * min(self.client_width, max_bounds.right - max_bounds.left), end="\x1b[0m")

        # if completely out of render, just skip all this goofy ah garbage
        if (
            max_bounds.left >= self.client_right or
            max_bounds.right < self.client_left or 
            max_bounds.top >= self.client_bottom or
            max_bounds.bottom < self.client_top
        ): return

        with Globals.__vis_document__.term.hidden_cursor():

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

                
                print(Globals.__vis_document__.term.move_xy(self.client_left, row) + fcode(self.style.get("color"), background=self.style.get("bg_color"), style=style_string) + text_left_padding*" " + text_chunk, end="\x1b[0m")
                text_chunk_index += 1

    def _determine_dimensions(partial_container_bounds: Boundary) -> Tuple[int, int]:
        """
        Given partial container dimensions (such as width=40px but height undefined),
        calculates what this element's width and height would be, regardless of position.
        
        This function is mainly for dealing with the fact that text elements change in 
        height based on length of text (if wrapping is on)
        """
        pass