import re
from shlex import split
from typing import List, Dict, TYPE_CHECKING
from document import Document
from div import Div
from text import Text

if TYPE_CHECKING:
    from common import Element
    from document import Document

TAG_TO_ELEMENT: Dict[str, "Element"] = {
    "div": Div,
    "text": Text,
}

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

def read(relative_filepath: str) -> Document:
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

        # if the tag is "/", move up one level
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

# test
doc = read("example.vis")
doc.mount()