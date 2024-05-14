from render.camera import Camera
import blessed
from render.constants import CameraUtils
from threading import Thread
from render.utils import fcode
from parser import parse_level
from engine.objects import OBJECTS, LevelObject

CURSOR_MOVEMENT_CHANGE = {"KEY_UP":[0, -1], "KEY_LEFT":[-1, 0], "KEY_DOWN":[0, 1], "KEY_RIGHT" :[1, 0]} #up:259 left:260 down:258 right:261
SCREEN_MOVEMENT_CHANGE = {"a":[0, -4], "d":[0, 4]}
CHANGE_OBJ = {"1": LevelObject(OBJECTS.spike, 0, 0), "2": LevelObject(OBJECTS.block, 0, 0), "3": LevelObject(OBJECTS.yellow_orb, 0, 0)}
OBJECT = ["block", "spike", "yellow_orb", "blue_orb", "purple_orb", "yellow_grav_portal", "blue_grav_portal"]
CURSOR_COLOR = "#68FF06"

class LevelEditor:

    def __init__(self):
        #self.level = [[]]
        self.level = parse_level("test2.level")
        self.term = blessed.Terminal()
        self.screen_pos = [0, 10]
        self.cursor_pos = CameraUtils.center_screen_coordinates(self.term)
        self.camera = Camera(self.level)
        self.cur_cursor_obj = None

    def movecamera(self, movement :str, cur: bool):
        if cur:
            self.cursor_pos[0] += CURSOR_MOVEMENT_CHANGE[movement][0]
            self.cursor_pos[1] += CURSOR_MOVEMENT_CHANGE[movement][1]
        else:
            self.screen_pos[1] += SCREEN_MOVEMENT_CHANGE[movement][1]

    def update_cursor_obj(self, obj):
        if obj not in CHANGE_OBJ:
            return
        self.cur_cursor_obj = CHANGE_OBJ[obj]

    def render(self):
        self.camera.level_editor_render(self.cursor_pos, self.screen_pos, self.cur_cursor_obj)

    def load_level_changes(self):
        self.camera.leveldata = self.level

    def start_editor(self):
        self.camera.render_init()
        self.render()
        running = True
        while running:
            with self.term.cbreak():
                val = self.term.inkey(timeout=None)
                if CURSOR_MOVEMENT_CHANGE.get(val.name) == None and SCREEN_MOVEMENT_CHANGE.get(val) == None and CHANGE_OBJ.get(val) == None:
                    if val == "q":
                        print("bye")
                        break
                else:
                    if CURSOR_MOVEMENT_CHANGE.get(val.name) != None:
                        self.movecamera(val.name, True)
                    elif CHANGE_OBJ.get(val) != None:
                        self.update_cursor_obj(val)
                    else:
                        self.movecamera(val, False)
                    self.render()
