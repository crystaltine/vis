from typing import TypedDict, Literal, Type

class TextStyleProps(TypedDict):
    """
    A schema of style options for text. No `top` or `bottom` because one line only.
    
    Left overrides right (if both not None, `right` is ignored). Cannot have both set to None.
    """
    color: str | tuple 
    bg_color: str | tuple
    bold: bool
    italic: bool
    underline: bool
    left: int
    right: int
    y: int
    text_align: Literal["left", "center", "right"]
    
    DEFAULT: "TextStyleProps" = {
        "color": "white",
        "bg_color": "transparent",
        "bold": False,
        "italic": False,
        "underline": False,
        "left": 0,
        "right": None, # calculated from "left" and text length
        "y": 0,
        "text_align": "left",
    }

print(type(TextStyleProps))
print(type(TextStyleProps.DEFAULT))
print(Type)

def test(a_typed_dict: Type) -> None:
    print(isinstance(a_typed_dict, Type))
    
test(TextStyleProps)