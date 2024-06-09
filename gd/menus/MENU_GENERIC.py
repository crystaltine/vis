from abc import ABC, abstractmethod
from typing import Literal
from logger import Logger
from render.camera_frame import CameraFrame
from render.texture_manager import TextureManager
from gd_constants import GDConstants
from blessed.keyboard import Keystroke

class GenericMenu(ABC):
    """ Abstract class for a implementing menus """
    
    @abstractmethod
    def render() -> None:
        """ Draw the current state of the menu to the screen """
        pass
        
    @abstractmethod
    def on_key(val: Keystroke) -> str | None:
        """ Handle a key press event, and send a signal back to MenuHandler if necessary. If not, sends back None. """
        pass
