from utils import convert_to_chars

class Boundary:
    """
    A helper class representing the boundaries of a generic container. Can be used for element rendering.
    
    Has the following fields, which are exact character values from the top-left corner of an arbitrary container:
    - `.left`
    - `.top`
    - `.right`
    - `.bottom`
    """
    
    left: int | None
    top: int | None
    right: int | None
    bottom: int | None
    
    def __init__(self, left: int = None, top: int = None, right: int = None, bottom: int = None):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
    
    @staticmethod
    def set_client_boundary(obj, container_bounds: "Boundary") -> None:
        """
        Sets the `.client_left`, `.client_top`, `.client_right`, `.client_bottom`, `.client_width`, and `.client_height`
        properties of the given object, given the container bounds. Uses the given object's styles (left, width, etc.) to do this.
        """
        
        container_width = container_bounds.right - container_bounds.left
        container_height = container_bounds.bottom - container_bounds.top
        
        l = obj.style.get("left")
        r = obj.style.get("right")
        t = obj.style.get("top")
        b = obj.style.get("bottom")
        w = obj.style.get("width")
        h = obj.style.get("height")
        
        true_t = convert_to_chars(container_height, t)
        true_b = convert_to_chars(container_height, b)  
        true_l = convert_to_chars(container_width, l)
        true_r = convert_to_chars(container_width, r)
        true_h = convert_to_chars(container_height, h)
        true_w = convert_to_chars(container_width, w)
        
        obj.client_top = container_bounds.top + (
            true_t if t is not None
            else container_bounds.bottom - true_b - true_h
        )
        obj.client_bottom = (
            container_bounds.bottom - true_b if b is not None
            else container_bounds.top + true_t + true_h
        )
        
        obj.client_left = container_bounds.left + (
            true_l if l is not None
            else container_bounds.right - true_r - true_w
        )
        obj.client_right = (
            container_bounds.right - true_r if r is not None
            else container_bounds.left + true_l + true_w
        )
        
        obj.client_width = obj.client_right - obj.client_left 
        obj.client_height = obj.client_bottom - obj.client_top
        