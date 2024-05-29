# MAJOR TODO: There are almost no errors in this interpreter, add those.
# also more flexibility with whitespaces i guess?

import re
from shlex import split
from typing import List, Dict, TYPE_CHECKING
from document import Document
from globalvars import Globals
from div import Div
from scrollbox import Scrollbox
from text import Text
from input import Input
from button import Button
from time import sleep

if TYPE_CHECKING:
    from element import Element
    from document import Document

TAG_TO_ELEMENT: Dict[str, "Element"] = {
    "div": Div,
    "text": Text,
    "input": Input,
    "button": Button,
    "scrollbox": Scrollbox
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

def read_vis(relative_filepath: str) -> None:
    """
    Parses a visage file and returns a `Document` object that represents it.
    
    Files are formatted similarly to HTML, but with a different tags.
    Also, the root tag can be any element. Most commonly, it's <div>.
    """
    code = ""
    with open(relative_filepath, "r") as f:
        code = f.read()
        f.close()
        
    # remove all newlines and tabs
    code = code.replace("\n", "")
    code = code.replace("\t", "")
    
    # split based on < and >
    tags: List[str] = re.split(r'[<>]+', code)
    """
    A list of "tags" that were parsed from the document.
    
    If the input code was 
    ```
    <div class=\"divclass-fdfdfse\" id=\"some random thing\">
        <text class=\"lol\" text=\"Hello!!!!!\"></>
        <text class=\"something\" text=\"Bye?\"></>
    </>
    ```
    
    `tags` should now be
    ```python
    [
        "div class=\"divclass-fdfdfse\" id=\"some random thing\"",
        "text class=\"lol\" text=\"Hello!!!!!\"",
        "/",
        "text class=\"lol2\" text=\"Hello!!!!!\"",
        "/"
        "/"
    ]
    ```
    """
    Globals.__vis_document__ = Document()
    current_element_path: "List[Document | Element]" = [Globals.__vis_document__]
    
    """ A list of the elements we are currently nested inside. Always begins with document. """

    #print("tags:", tags)

    for tag in tags:
        
        tag = tag.strip()

        # if the tag is "/" (end tag), move up one level
        if tag.startswith("/"):
            current_element_path.pop()
            continue
        
        if not current_element_path[-1].SUPPORTS_CHILDREN:
            raise VisInterpreterError(f"Element {current_element_path[-1]} does not support children.")

        tokens = split(tag) # this splits by spaces but keeps nested strings intact (e.g. class strings)
        #print(f"Tokens: {tokens}, split from tag: {tag}")
        
        if len(tokens) == 0: continue # probably whitespace

        # now we might have something like this
        # tokens = ['div', 'class=class1 class2 class3', 'id=some-random-id']

        attrs = {}
        tag_name, tag_attrs = tokens[0], tokens[1:]

        #print(f"tag attrs: {tag_attrs}")
        for attr_definition in tag_attrs:
            # each one of these is like "class=class1 class2 class3"
            # attr name is .split()[0]
            
            #print(f"\x1b[31mLooping thru attr_defs for tagname={tag_name}, attr_def={attr_definition}\x1b[0m")
            attr_name, attr_params = attr_definition.split("=", maxsplit=1)
            attrs[attr_name] = attr_params
            #print(f"^Setting attrs[{attr_name}] to {attr_params}")

        element = create_element(tag_name, attrs)
        #print(f"\x1b[33mCreated element: {element}\x1b[0m")
        
        # add the element as a child of the current element                
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
        background_color: blue,
    }
    ```
    
    Sets the styles into the global scope. Returns None.
    """

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
            # try to get new class definition. This is a list of class names we are defining
            currently_defining = line.split("{")[0].strip().split(",")
            
        else:
            
            # exit if we are done defining this(or these) classes
            if line.strip() == "}":
                currently_defining = []
                continue
            
            # otherwise, we are currently defining styles. This line should be a style property
            split_property_def = line.strip().split(":")
            #print(f"Style parser: defining a style prop: {split_property_def}")
            
            # if not 2 parts, then error
            if len(split_property_def) != 2:
                raise VisInterpreterError(f"Invalid style property definition (exactly one per line): {line.strip()}")
            
            # add the property to the class
            for classname in currently_defining:
                
                real_classname = classname[1:] # since classname defs are like .classname
                
                if real_classname not in Globals.__class_styles__:
                    Globals.__class_styles__[real_classname] = {}
                    
                value_to_set = split_property_def[1].strip()
                
                # catching some shorthands/compatibility
                if value_to_set == "None": value_to_set = None
                if value_to_set in ["0", 0]: value_to_set = "0ch" # units not required for 0
                    
                Globals.__class_styles__[real_classname][split_property_def[0].strip()] = value_to_set
                
    #print(f"Class styles: {Globals.__class_styles__}")

# test
#read_styles("example.tss")
#read_vis("example.vis")
#
#document = Globals.__vis_document__
#
#document.mount()

#document.get_element_by_id("messages_pane").add_child(Text(text="HELLO"))

