from abc import abstractmethod
from typing import Dict, TypedDict, TYPE_CHECKING, Unpack
from utils import parse_class_string, parse_style_string, calculate_style

if TYPE_CHECKING:
    from document import Document
    
class Element:
    """
    An abstract class representing a generic element in the component tree.
    """
    
    class Attributes(TypedDict):
        """
        A base schema of props for creating a generic element.
        Most elements will have additional props.
        """
        id: str | None
        class_str: str | None
        style_str: str | None

    class StyleProps(TypedDict):
        """ Generic, abstract subclass defining ALL supported style options for the element """
        ...
    
    SUPPORTS_CHILDREN: bool
    """ @static @constant - Whether or not the element supports children. """
    DEFAULT_STYLE: Dict[str, str]
    """ @static @constant - The default style options for all instances of the element. """
    
    document: "Document"
    """ A reference to the root document object the element is rendered on. This is for thing like event handler registration. """
    
    id: str | None
    """ An identifier for the element, which can be used to reference it (using `Document.get_element_by_id`) """
    
    is_selected: bool = False
    """ Whether or not the element is currently selected. """
    
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
        self.document = globals()["__vis_document__"]
        self._class_str = attrs.get("class_str", "")
        self._style_str = attrs.get("style_str", "")
        self.id = attrs.get("id", None)
        self.is_selected = False
        self.client_left = None
        self.client_top = None
        self.client_right = None
        self.client_bottom = None
        
        # calculate initial style
        self.style = calculate_style(self.style_str, self.class_str, self.DEFAULT_STYLE)
        self.style: self.__class__.StyleProps # typecast for convenience

    @abstractmethod
    def render(self, container_left: int, container_top: int, container_right: int, container_bottom: int) -> None:
        """ 
        Renders the element to its container at the specified position, 
        given the positions of the container. Applies the most recently updated style. """
        ...
