from element import Element
from utils import fcode, convert_to_chars, print2, len_no_ansi, remove_ansi
from typing import Literal, Unpack, Callable, TYPE_CHECKING
from globalvars import Globals
from boundary import Boundary
from time import time
from logger import Logger

if TYPE_CHECKING:
    from key_event import KeyEvent2
    
class Input(Element):
    """
    An editable text field
    """
    
    class Attributes(Element.Attributes):
        """ All special props that can be used for creating an input element. """
        id: str | None
        class_str: str | None
        style_str: str | None
        on_enter: Callable[["Input"], None]
        placeholder: str | None
        max_len: int | None
        pattern: str | None
        container_bg: str

    class StyleProps(Element.StyleProps):
        """ A schema of style options for input elements. """
        position: str
        visible: bool
        color: str | tuple 
        placeholder_color: str | tuple
        cursor_bg_color: str | tuple
        cursor_fg_color: str | tuple
        bg_color: str | tuple
        hovered_bg_color: str | tuple
        selected_bg_color: str | tuple
        bold: bool
        italic: bool
        underline: bool
        padding_top: int
        padding_right: int
        padding_bottom: int
        padding_left: int
        padding: int
        left: int
        right: int | None
        width: int
        y: int
        text_align: Literal["left", "center", "right"]
        hoverable: bool
        selectable: bool
        hide_input: bool | None
        
    SUPPORTS_CHILDREN = False
    DEFAULT_STYLE: "StyleProps" = {
        "position": "relative",
        "visible": True,
        "color": "black",
        "placeholder_color": "gray",
        "cursor_bg_color": "black",
        "cursor_fg_color": "white",
        "bg_color": "white",
        "hovered_bg_color": (230, 230, 230),
        "selected_bg_color": (190, 190, 210),
        "bold": False,
        "italic": False,
        "underline": False,
        "padding_top": 0,
        "padding_right": 0,
        "padding_bottom": 0,
        "padding_left": 0,
        "padding": 0,
        "left": 0,
        "width": 10,
        "top": 0,
        "height": 1,
        "text_align": "left",
        "hoverable": True,
        "selectable": True,
        "hide_input": False,
    }
    
    def __init__(self, **attrs: Unpack["Attributes"]):
        """
        Attributes:
        - id: str | None
        - class_str: str | None
        - style_str: str | None
        - on_enter: Callable[[Input], None] (passes in pointer to this input object)
        - placeholder: str | None
        - max_len: int | None
        - pattern: str | None
        """
        
        super().__init__(**attrs)

        self.placeholder = attrs.get("placeholder", "")
        self.max_len = attrs.get("max_len", None)
        self.curr_text: str = ""
        self.cursor_pos = 0
        self.on_enter = attrs.get("on_enter", lambda x: None)
        """ Callback for when user presses enter and this element is selected. """

        self.insert_mode = False
        """ If typing a character should replace or insert, if cursor is not at the end of the curr string. Toggled with the INS key."""

        self.text_left_index = 0
        """ Represents the index of the leftmost character to render, in case of overflow """
        
        # assert that not both left and right are None
        assert not (self.style.get("left") is None and self.style.get("right") is None), "[Text]: At least one of left or right must not be None."

        def _event_handler(e: "KeyEvent2"):
            """ 
            Should only run when the element is selected.
            Internal event handler for document keydown events (for typing inside the element) 
            """

            # else, handle key.
            if not e.is_special:
                self._insert_char(e.key)

            else:
                if e.name == 'KEY_BACKSPACE':
                    self._backspace()

                elif e.name == 'KEY_DELETE':
                    self._delete()

                elif e.name == "KEY_INSERT":
                    self.insert_mode = not self.insert_mode

                elif e.name == 'KEY_LEFT':
                    self._move_left()
                
                elif e.name == 'KEY_RIGHT':
                    self._move_right()

                elif e.name == 'KEY_ENTER':
                    self.on_enter(self)

                elif e.name == 'KEY_ESCAPE':
                    self.curr_text = ""
                    # return or something/deselect (same as enter) (TODO)

                elif e.name == 'KEY_TAB':
                    # deselect BUT go to next element (handled by document FOR NOW) (TODO?)
                    pass

                #Logger.log(f"Input: special key {e.key}: curr_text is now {self.curr_text}, curs_pos is {self.cursor_pos}")
            
            self.render()

        # register this element's event handler with the document's special handlers
        Globals.__vis_document__.element_key_listeners[self] = set([_event_handler])
        if self.style.get("selectable"): Globals.__vis_document__.selectable_elements.add(self)
        if self.style.get("hoverable"): Globals.__vis_document__.hoverable_elements.add(self)

    def _insert_char(self, char: str):
        """
        Internal helper function. Handles changing this input element's value, scrolling, cursor moving, etc.
        based on the current cursor position. Does absoluely nothing if curr text is already at max_len before inserting.
        """
        if self.max_len is not None and len(self.curr_text) >= self.max_len:
            return

        self.curr_text = self.curr_text[:self.cursor_pos] + char + self.curr_text[self.cursor_pos+(int(self.insert_mode)):]
        
        # always move cursor up one
        self.cursor_pos += 1

        # scroll right 1 unit if overflowing AND cursor is at the rightmost edge
        #Logger.log(f"Input's _insert_char: if statement for incrementing text_left_idx: {len(self.curr_text)=} >= {self.client_width=} AND {self.cursor_pos=} - {self.text_left_index=} >= {self.client_width=}")
        if (len(self.curr_text) >= self.client_width) and (self.cursor_pos - self.text_left_index >= self.client_width):
            self.text_left_index += 1

        #Logger.log(f"input ele: inserted '{char}' into '{self.curr_text}', cursor_pos is now {self.cursor_pos}, text_left_index is now {self.text_left_index}")

    def _backspace(self):
        """
        Run backspace at current cursor position. Also adjusts the scrolling
        if resulting text is still longer than the element width (scrolls back toward idx 0)
        """
        # assertion: cursor_pos in [0, len(curr text)]
        # thus, we need to clip cursor_pos-1 to 0
        self.curr_text = self.curr_text[:max(0,self.cursor_pos-1)]+self.curr_text[self.cursor_pos:]
        self.cursor_pos = max(0, self.cursor_pos - 1)

        # if length of text longer than element width, decrement leftpos (scrolling back toward beginning of text)
        if len(self.curr_text) > self.client_width:
            self.text_left_index = max(0, self.text_left_index-1)

    def _delete(self):
        # assertion: cursor_pos in [0, len(curr text)]
        # thus, we need to clip cursor_pos+1 to len(curr text)
        self.curr_text = self.curr_text[:self.cursor_pos]+self.curr_text[min(len(self.curr_text),self.cursor_pos+1):]

    def _move_left(self):
        """
        Moves cursor left by one char (simulates left arrow press), handles scrolling, etc.
        """
        self.cursor_pos = max(0, self.cursor_pos - 1)

        # if we hit the left arrow at the leftmost index of the currently displayed text, scroll left
        if self.cursor_pos < self.text_left_index:
            self.text_left_index -= 1

    def _move_right(self):
        # capped at 1 after the last character
        self.cursor_pos = min(len(self.curr_text), self.cursor_pos + 1)

        relative_cursor_pos = self.cursor_pos - self.text_left_index

        # if we go past the rightmost char, then scroll right
        if relative_cursor_pos >= self.client_width:
            self.text_left_index += 1

    def clear(self) -> None:
        """ Clears current text of the element, and rerenders it. """
        self.curr_text = ""
        self.cursor_pos = 0
        self.render()

    def render(self, container_bounds: Boundary = None, container_bg: str = None):

        ##Logger.log(f"<BEGIN INPUT render func>: this element is hovered: {Globals.is_hovered(self)}, this element is active: {Globals.is_active(self)}")
        container_bounds = self.get_true_container_edges(container_bounds)
        Boundary.set_client_boundary(self, container_bounds)
        
        if not self.style.get("visible"): return
        
        # ======================= #
        # TEXT STYLE CALCULATIONS #
        # ======================= #

        #Logger.log(f"[t={time()}]: about to print some random stuff from input render()")
        #print(f"{Globals.__vis_document__.term.move_xy(4, 4)}inside input render()")

        style_string = " ".join([
            "bold" if self.style.get("bold") else "",
            "italic" if self.style.get("italic") else "",
            "underline" if self.style.get("underline") else ""
        ])
        bg_color_to_use = self.style.get(
            "bg_color" if (not Globals.is_active(self)) and (not Globals.is_hovered(self))
            else "hovered_bg_color" if Globals.is_hovered(self)
            else "selected_bg_color"
        )
        regular_text_fcode = fcode(self.style.get("color"), background=bg_color_to_use, style=style_string)
        cursor_fcode = fcode(self.style.get("cursor_fg_color"), background=self.style.get("cursor_bg_color"), style=style_string) if Globals.is_active(self) else regular_text_fcode
        placeholder_fcode = fcode(self.style.get("placeholder_color"), background=bg_color_to_use, style=style_string)

        # ============== #
        # RENDERING TEXT #
        # ============== #

        visible_text = (
            self.curr_text[self.text_left_index:min(self.text_left_index+self.client_width, len(self.curr_text))] if not self.style.get("hide_input")
            else (min(self.text_left_index+self.client_width, len(self.curr_text))-self.text_left_index)*"*"
        )
        text_to_render = ...

        if self.curr_text:

            if self.cursor_pos == len(self.curr_text):
                #Logger.log(f"calcing text to render in input: cursor at end, {self.text_left_index=}, {visible_text=}, {self.cursor_pos=}")
                # special case where the cursor is at the end
                text_to_render = (
                    # splicing the string to highlight the cursor
                    regular_text_fcode + visible_text[:self.cursor_pos-self.text_left_index] + 
                    cursor_fcode + " "
                )
            else:
                #Logger.log(f"calcing text to render in input: cursor not at end, {self.text_left_index=}, {visible_text=}, {self.cursor_pos=}")
                # the user changed the cursor pos, now it is somewhere in the middle of the text
                text_to_render = (
                    # splicing the string to highlight the cursor:
                    # 0 -> cursor_pos - text_left_index - 1: regular text
                    # cursor_pos - text_left_index: cursor
                    # cursor_pos - text_left_index + 1 -> end: regular text
                    regular_text_fcode + visible_text[:self.cursor_pos-self.text_left_index] + 
                    cursor_fcode + visible_text[self.cursor_pos-self.text_left_index] +
                    regular_text_fcode + visible_text[self.cursor_pos-self.text_left_index+1:]
                )

        else:
            if Globals.is_active(self):
                if len(self.placeholder) > 0:
                    text_to_render = cursor_fcode + self.placeholder[0] + placeholder_fcode + self.placeholder[1:(self.client_right-self.client_left)]
                else: 
                    text_to_render = cursor_fcode + " "
            else:
                # if not selected, render placeholder
                text_to_render = placeholder_fcode + self.placeholder[:self.client_right-self.client_left]
        text_to_render += regular_text_fcode + " "*(self.client_width - len_no_ansi(text_to_render))
        #Logger.log(f"Input renderer: final stripped text_to_render is {remove_ansi(text_to_render)}")

        #with Globals.__vis_document__.term.hidden_cursor():
        print2(Globals.__vis_document__.term.move_xy(self.client_left, self.client_top) + text_to_render)