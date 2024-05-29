from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from document import Document

class Globals:
    """
    A class containing global variables, such as the document and style.
    """
    __vis_document__: "Document" = None
    """
    Currently active document. Initialized by `interpreter.py` and is used in all child components.
    """

    __class_styles__: dict[str, dict[str, str]] = {}
    """
    Dict of classnames : style dicts parsed from .tss files.
    """
    
    def is_active(object) -> bool:
        """
        Returns whether or not the given object is the currently active element
        in the document (`__vis_document__.active`)
        """
        return object is Globals.__vis_document__.active
    
    def is_hovered(object) -> bool:
        """
        Returns whether or not the given object is the currently hovered element
        in the document (`__vis_document__.hovered`)
        """
        return object is Globals.__vis_document__.hovered