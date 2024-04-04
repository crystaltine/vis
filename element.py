from abc import abstractmethod
from typing import Tuple, Dict, Literal, TypedDict, TYPE_CHECKING, Unpack
from utils import parse_class_string, parse_style_string, calculate_style
from globalvars import Globals
from logger import Logger

if TYPE_CHECKING:
    from document import Document
    
class Element:
    """
    An abstract class representing a generic element in the component tree.
    """
    
    class Attributes(TypedDict):
        """
        All props that can be provided when creating an element.
        """
        ...

    class StyleProps(TypedDict):
        """ Generic, abstract subclass defining ALL supported style options for the element """
        ...
    
    SUPPORTS_CHILDREN: bool
    """ @static @constant - Whether or not the element supports children. """
    DEFAULT_STYLE: Dict[str, str]
    """ @static @constant - The default style options for all instances of the element. """
    
    id: str | None
    """ An identifier for the element, which can be used to reference it (using `Document.get_element_by_id`) """

    style: Dict[str, str]
    """ A dict of the currently active style options for the element, a combination of default, class, and explicit styles. 
    Should be up-to-date with any dynamic styling. """
    
    _class_str: str
    """ The class string that was last set on the element. Use `class_str` property instead of this. """
    
    _style_str: str
    """ The style string that was last set on the element. Use `style_str` property instead of this. """
    
    client_left: int | None
    """ The absolute x-position of the left of the element on the screen. 
    0 is the left edge of the screen. is `None` if element hasn't been rendered yet. """
    
    client_top: int | None
    """ The absolute y-position of top the of the element on the screen. 
    0 is the top edge of the screen. is `None` if element hasn't been rendered yet."""
    
    client_right: int | None
    """ 1 + the absolute x-position of the right of the element on the screen. 
    0 is still the left edge of the screen. (notice the +1). is `None` if element hasn't been rendered yet. """
    
    client_bottom: int | None
    """ 1 + the absolute y-position of the bottom of the element on the screen. 
    0 is still the top edge of the screen. (notice the +1). is `None` if element hasn't been rendered yet. """
    
    # class_str, a property
    @property
    def class_str(self) -> str:
        """ A space-separated string of class names that should be applied to the element. """
        return self._class_str
    
    @class_str.setter
    def class_str(self, value: str) -> None:
        self._class_str = value
        self.style = parse_class_string(value) | self.style
        
    @property
    def style_str(self) -> str:
        """ Explicit style properties that should be applied to the element. """
        return self._style_str
    
    @style_str.setter
    def style_str(self, value: str) -> None:
        self._style_str = value
        self.style = parse_style_string(value) | self.style

    def __init__(self, **attrs: Unpack["Attributes"]) -> None:        
        self._class_str = attrs.get("class_str", "")
        self._style_str = attrs.get("style_str", "")
        
        Logger.log(f"\x1b[32mElement init: _class_str is {self._class_str}, _style_str is {self._style_str}\x1b[0m")
        
        self.id = attrs.get("id", None)
        
        self.last_remembered_container = []
        """ Stores the `[left, top, right, bottom]` of the last container the element was rendered in. Can be used for efficient re-rendering. """

        self.client_left = None
        self.client_top = None
        self.client_right = None
        self.client_bottom = None

        self.last_remembered_container = [None] * 4
        
        # calculate initial style
        self.style = calculate_style(self.style_str, self.class_str, self.DEFAULT_STYLE)
        
        if self.id:
            if self.id in Globals.__vis_document__.id_map:
                raise ValueError(f"Cannot add {self} to Document: an element with id '{self.id}' already exists.")
            else: Globals.__vis_document__.id_map[self.id] = self

        if getattr(self.style, "selectable", False):
            Globals.__vis_document__.selectable_elements.add(self)
    
    def __str__(self) -> str:
        return f"<Element:{self.__class__.__name__} {self.class_str=} {self.id=} {self.style=}>"

    @abstractmethod
    def render(self, container_left: int = None, container_top: int = None, container_right: int = None, container_bottom: int = None) -> None:
        """ 
        Renders the element to its container at the specified position, 
        given the positions of the container**. Applies the most recently updated style. 
        
        ### **IMPORTANT: 
        For any container dimension that isn't provided, attempts to use the last memorized container. 
        If that is unavailable as well, throws an error.
        
        ### IMPORTANT 2: 
        If the element has position: absolute, completely ignores all the container-related
        stuff and uses the entire screen as the container.
        """
        ...
        
    def get_true_container_edges(self, container_left: int | None, container_top: int | None, container_right: int | None, container_bottom: int | None) -> Tuple[int, int, int, int]:
        """
        Handles all the dirty memorized container, absolute positioning, unprovided dimensions, etc. stuff,
        returns a tuple of the true container dimensions to use in rendering: 
        `(container_left, container_top, container_right, container_bottom)`.
        
        If an element's positioning is absolute when this function is called,
        it will ignore the container dimensions and use the entire screen as the container.
        However, it will NOT update the last remembered container to be the entire screen.
        
        Updates the element's last_remembered_container attribute if the element's position is relative.
        
        ### USAGE:
        
        Should be called at the beginning of every element.render() method that needs to know its container.
        
        Use like this:
        ```python
        container_left, container_top, container_right, container_bottom = self.get_true_container_edges(container_left, container_top, container_right, container_bottom)
        ```
        
        Then you can do things with those values, like drawing the element, calculating width, height, etc.
        """
        # update last remembered container
        self.last_remembered_container = [
            container_left if container_left is not None else self.last_remembered_container[0],
            container_top if container_top is not None else self.last_remembered_container[1],
            container_right if container_right is not None else self.last_remembered_container[2],
            container_bottom if container_bottom is not None else self.last_remembered_container[3]
        ]
        
        container_left = self.last_remembered_container[0] if self.style.get("position") == "relative" else 0
        container_top = self.last_remembered_container[1] if self.style.get("position") == "relative" else 0
        container_right = self.last_remembered_container[2] if self.style.get("position") == "relative" else Globals.__vis_document__.term.width
        container_bottom = self.last_remembered_container[3] if self.style.get("position") == "relative" else Globals.__vis_document__.term.height
        
        Logger.log(f"Element's get_true_container_edges: \n^^^ MEMORIZED:{self.last_remembered_container=}")
        
        return container_left, container_top, container_right, container_bottom

    def get_center(self, format: Literal["xy", "yx"] = "xy") -> Tuple[int, int]:
        """
        Returns a tuple of integer coordinates for the CENTER of the element (rounded up if odd)
        
        By default, returns in the format `(x, y)`, where 
        `x` is horizontal distance (characters from left of screen, with leftmost col being x=0)
        and `y` is vertical distance (characters from top of screen, with first row being y=0)

        Specify format as either `xy` or `yx`. Default `xy`. If something is provided but it isn't
        either one of those two, returns the default, `(x, y)`.
        """

        x = round((self.client_left + self.client_right)/2)
        y = round((self.client_top + self.client_bottom)/2)

        return y,x if format == 'yx' else x,y
