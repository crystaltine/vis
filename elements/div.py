from vis.element import Element
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from vis.tss import TSSProperties

DIV_DEFAULT_PROPERTIES = TSSProperties(pre={

}

class Div(Element):
    """
    Implementation of a vis element resembling the HTML div element.
    """

    def __init__(self, children: List["Element"] = [], style: TSSProperties = None):
        super().__init__(children, style)