from typing import TYPE_CHECKING
from render.texture_manager import TextureManager
from render.camera_frame import CameraFrame
from level import Level

if TYPE_CHECKING:
    from blessed.keyboard import Keystroke

class LevelSettingsPopup:
    """ stuff for rendering the level settings popup (edit starting colors, starting gamemode, speed, song, etc.) """
    def __init__(self, level: Level):
        self.level = level
        
    def render(self, frame: CameraFrame):
        """ Draws this popup to the center of the frame provided, and renders the frame. """
        pass
    
    def handle_key(self, key: "Keystroke") -> bool:
        """ Performs actions on this instance based on key pressed. Returns True if popup closed, False otherwise. """
        pass
    