import re
from typing import List, TYPE_CHECKING
from document import Document
from common import Element
from div import Div
from text import Text

if TYPE_CHECKING:
    from document import Document
    
def create_element(tag: str, attrs: dict) -> "Element":
    pass

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
    
    tags
    
    curr_index = 0
    current_element_path = [__vis_document__]
    """ A list of the elements we are currently nested inside. Always begins with document. """

# test
doc = read("example.vis")
doc.mount()