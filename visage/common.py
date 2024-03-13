from abc import abstractmethod
from typing import TypedDict, TYPE_CHECKING
from utils import parseattrs, parse_style_string

if TYPE_CHECKING:
    from document import Document

class ElementAttributes(TypedDict):
    """
    A schema of props for creating a generic element.
    """
    id: str | None
    class_str: str | None
    style_str: str | None

class Element:
    """
    An abstract class representing a generic element in the component tree.
    """
    
    SUPPORTS_CHILDREN: bool
    """ @static @constant - Whether or not the element supports children. """
    DEFAULT_STYLE: dict[str, str]
    """ @static @constant - The default style options for all instances of the element. """
    
    document: "Document"
    """ A reference to the root document object the element is rendered on. This is for thing like event handler registration. """
    
    id: str | None
    """ An identifier for the element, which can be used to reference it (using `Document.get_element_by_id`) """
    
    class_list: list[str]
    """ A list of classes that the element belongs to. """
    
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

    def __init__(self, **attrs) -> None:
        
        # style dict that merges the default style with the provided style (provided takes precedence)
        style_dict = self.__class__.DEFAULT_STYLE | parse_style_string(attrs.get("style_str"))

        parseattrs(self, style_dict, self.__class__.DEFAULT_STYLE)
        
        self.document = globals()["__vis_document__"]
        self.class_list = (cs := attrs.get("class_str")).split(" ") if cs else []
        self.id = id
        self.client_left = None
        self.client_top = None
        self.client_right = None
        self.client_bottom = None

    @abstractmethod
    def render(self, container_left: int, container_top: int, container_right: int, container_bottom: int) -> None:
        """ Renders the element to its container at the specified position, given the positions of the container. """
        ...
