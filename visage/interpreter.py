# MAJOR TODO: There are almost no errors in this interpreter, add those.
# also more flexibility with whitespaces i guess?

import re
from shlex import split
from typing import List, Dict, TYPE_CHECKING
from document import Document
from div import Div
from text import Text
from input import Input

if TYPE_CHECKING:
    from element import Element
    from document import Document

TAG_TO_ELEMENT: Dict[str, "Element"] = {
    "div": Div,
    "text": Text,
    "input": Input
}

class VisInterpreterError(Exception):
    pass

def create_element(tag: str, attrs: dict) -> "Element":
    """
    Returns an `Element` object based on the provided tag (name) with the specified attributes.
    Example attributes dict:
    ```python
    attrs = {
        "class": "class1 class2 class3",
        "id": "some-unique-element-id",
    }
    ```

    Throws `KeyError` if the specified tag is not supported. 
    """

    return TAG_TO_ELEMENT[tag](**attrs)

def read_vis(relative_filepath: str) -> Document:
    """
    Parses a visage file and returns a `Document` object that represents it.
    
    Files are formatted similarly to HTML, but with a different tags.
    Also, the root tag can be any element. Most commonly, it's <div>.
    """
    code = ""
    with open(relative_filepath, "r") as f:
        code = f.read()
        f.close()
        
    # remove all newlines
    code = code.replace("\n", "")
    
    # create document
    global __vis_document__
    __vis_document__ = Document()
    
    # split based on < and >
    tags: List[str] = re.split(r'[<>]+', code)
    """
    A list of "tags" that were parsed from the document.
    
    If the input code was 
    ```
    <div class=\"divclass-fdfdfse\" id=\"some random thing\">
        <text class=\"lol\">Hello!!!!!</>
        <text class=\"lol2\">Bye!!!!!</>
    </>
    ```
    
    `tags` should now be
    ```python
    [
        "div class=\"divclass-fdfdfse\" id=\"some random thing\"",
        "text class=\"lol\"",
        "Hello!!!!!",
        "/",
        "text class=\"lol2\"",
        "Bye!!!!!",
        "/"
        "/"
    ]
    ```
    """
    
    curr_index = 0
    current_element_path = [__vis_document__]
    """ A list of the elements we are currently nested inside. Always begins with document. """

    for tag in tags:

        # if the tag is "/" (end tag), move up one level
        if tag.startswith("/"):
            current_element_path.pop()
            continue

        tokens = split(tag) # this splits by spaces but keeps nested strings intact (e.g. class strings)

        # now we might have something like this
        # tokens = ['div', 'class=class1 class2 class3', 'id=some-random-id']

        attrs = {}
        tag_name, tag_attrs = tokens[0], tokens[1:]

        for attr_definition in tag_attrs:
            # each one of these is like "class=class1 class2 class3"
            # attr name is .split()[0]
            attr_name, attr_params = attr_definition.split(maxsplit=1)
            attrs[attr_name] = attr_params

        element = create_element(tag_name, attrs)
        current_element_path[-1].add_child(element)
        current_element_path.append(element)

def read_styles(relative_filepath: str) -> None:
    """
    Parses a .tss file of the format:
    ```
    .class_name {
        background_color: red
        left: 20ch
        top: 10ch
        width: 50ch
        height: "50ch
    }

    .class2, .class3 {
        "background_color": "blue",
    }
    ```
    """
    
    global class_styles # accessible from anywhere in the module, specifically in `./utils.py`
    class_styles: Dict[str, dict] = {}
    """ class name -> style properties """
    
    lines = []
    with open(relative_filepath, "r") as f:
        lines = f.readlines()
        f.close()

    # process lines for each line
    # strip, then split by space. First n-1 elements are the class names, last should be the opening brace
    # then keep parsing until we find the closing brace
    currently_defining = []
    """ list of classnames we are currently defining. Empty means search for new class definition header. """
    
    for line in lines:
        if not line.strip():
            continue
            
        if not currently_defining:
            # try to get new class definition
            currently_defining = line.split("{")[0].strip().split(",")
            
        else:
            
            # exit if we are done defining this class
            if line.strip() == "}":
                currently_defining = []
                continue
            
            # we are currently defining a class. This line should be a style property
            split_property_def = line.strip().split(":")
            
            # if not 2 parts, then error
            if len(split_property_def) != 2:
                raise VisInterpreterError(f"Invalid style property definition (exactly one per line): {line.strip()}")
            
            # add the property to the class
            for classname in currently_defining:
                if classname not in class_styles:
                    class_styles[classname] = {}
                    
                class_styles[classname][split_property_def[0].strip()] = split_property_def[1].strip()

# test
read_styles("example.tss")
doc = read_vis("example.vis")
doc.mount()