import blessed
from threading import Thread, Timer
from copy import deepcopy
from render.camera import Camera
from render.constants import CameraUtils
from render.utils import fcode
from parse_level import parse_level
from logger import Logger
from run_gd import run_level
from engine.objects import OBJECTS, LevelObject
import time

CURSOR_MOVEMENT_CHANGE = {"KEY_UP":[0, -1], "KEY_LEFT":[-1, 0], "KEY_DOWN":[0, 1], "KEY_RIGHT" :[1, 0]}
SCREEN_MOVEMENT_CHANGE = {"a":[-4, 0], "d":[4, 0]}
CHANGE_OBJ = {"1": LevelObject(OBJECTS.spike, 0, 0), "2": LevelObject(OBJECTS.block0_0, 0, 0), "3": LevelObject(OBJECTS.yellow_orb, 0, 0), "4": LevelObject(OBJECTS.blue_orb, 0, 0), "5": LevelObject(OBJECTS.purple_orb, 0, 0)}
OBJECT = ["block", "spike", "yellow_orb", "blue_orb", "purple_orb", "yellow_grav_portal", "blue_grav_portal"]
CURSOR_COLOR = "#68FF06"

class LevelEditor:

    def __init__(self):
        self.level = parse_level("test2.level")
        self.level_name = "" # We should use this later to specify name for saving and loading menu ui instead of manually specifying a name in backend
        self.term = blessed.Terminal()
        self.screen_pos = [0, 0]
        self.cursor_pos = CameraUtils.center_screen_coordinates(self.term)
        self.camera = Camera(self.level)
        self.cur_cursor_obj = None
        self.del_list = []
        self.undo_stack = []
        self.autosave_interval = 300  # Autosave interval in seconds (5 minutes)
        self.autosave_thread = Thread(target=self.autosave_loop)
        self.autosave_thread.daemon = True
        self.autosave_thread.start()
    
    def autosave_loop(self):
        while True:
            time.sleep(self.autosave_interval)
            self.save_level("levels/basic.auto")

    def movecamera(self, movement: str, cur: bool):
        if cur:
            self.cursor_pos[0] += CURSOR_MOVEMENT_CHANGE[movement][0]
            self.cursor_pos[1] += CURSOR_MOVEMENT_CHANGE[movement][1]
        else:
            self.cursor_pos[0] -= SCREEN_MOVEMENT_CHANGE[movement][0]
            self.screen_pos[0] += SCREEN_MOVEMENT_CHANGE[movement][0]

    def update_cursor_obj(self, obj):
        if obj not in CHANGE_OBJ:
            return
        self.cur_cursor_obj = CHANGE_OBJ[obj]

    def render(self):
        self.camera.level_editor_render(self.cursor_pos, self.screen_pos, self.cur_cursor_obj)

    def place_object(self):
        Logger.log(f"place_obj, {self.cur_cursor_obj=}")
        if self.cur_cursor_obj is not None:
            x, y = self.cursor_pos
            grid_x, grid_y = x + self.screen_pos[0] - CameraUtils.CAMERA_LEFT_OFFSET, y + self.screen_pos[1]
            Logger.log(f"^ {self.cursor_pos=}, gridx/gridy:{grid_x}/{grid_y} len(level)={len(self.level)}")
            if 0 <= grid_y < len(self.level) and 0 <= grid_x < len(self.level[grid_y]):
                # Store current state for undo
                self.undo_stack.append(deepcopy(self.level))
                self.level[grid_y][grid_x] = (a:=LevelObject(self.cur_cursor_obj.data, grid_x, grid_y))
                self.load_level_changes()  # Update camera's leveldata
                self.render()
                Logger.log(f"placing obj: {a}, ")
   

    def delete_object(self):
        x, y = self.cursor_pos
        grid_x, grid_y = x + self.screen_pos[0] - CameraUtils.CAMERA_LEFT_OFFSET, y + self.screen_pos[1]
        Logger.log(f"^ {self.cursor_pos=}, gridx/gridy:{grid_x}/{grid_y} len(level)={len(self.level)}")
        if 0 <= grid_y < len(self.level) and 0 <= grid_x < len(self.level[grid_y]):
            # Store current state for undo
            self.undo_stack.append(deepcopy(self.level))
            self.del_list.append(self.level[grid_y][grid_x].data)
            self.level[grid_y][grid_x] = LevelObject(None, grid_x, grid_y)
            self.load_level_changes()  # Update camera's leveldata
            self.render()

    def load_level(self, filename: str):
        # Loads level (input broken)
        self.level = parse_level("levels/" + filename)
        self.level_old = deepcopy(self.level)
        self.load_level_changes()
        self.render()

    def all_clear(self):
        # Clear level data
        self.undo_stack.append(deepcopy(self.level))
        self.level = parse_level("basic.level")
        self.load_level_changes()
        self.render()

    def undo(self):
        if self.undo_stack:
            # Pop previous state from undo stack and restore it
            self.level = self.undo_stack.pop()
            self.load_level_changes()
            self.render()

    def load_level_changes(self):
        self.camera.leveldata = self.level

    def save_level(self, filename: str):
        symbol_map = {
            "block": 'x',
            "spike": '^',
            "yellow_orb": 'y',
            "blue_orb": 'b',
            "purple_orb": 'p'
        }
        with open(filename, 'w') as f:
            for row in self.level:
                line = ''
                for item in row:
                    if item.data is None:
                        line += ' '  # Assuming empty spaces are represented by a space character
                    else:
                        line += symbol_map.get(item.data["name"], '?')  # Use '?' as a default for unknown objects
                f.write(line + '\n')
        print(f"Level saved as {filename}")

    def increase_height(self):
        self.undo_stack.append(deepcopy(self.level))
        width = len(self.level[0]) if self.level else 10
        new_row = [LevelObject(None, x, len(self.level)) for x in range(width)]
        self.level.insert(0,new_row)
        self.load_level_changes()
        self.render()

    def decrease_height(self):
        self.undo_stack.append(deepcopy(self.level))
        if self.level:
            self.level.pop(0)
            self.load_level_changes()
            self.render()

    def increase_length(self):
        self.undo_stack.append(deepcopy(self.level))
        for row in self.level:
            row.append(LevelObject(None, len(row), self.level.index(row)))
        self.load_level_changes()
        self.render()

    def decrease_length(self):
        self.undo_stack.append(deepcopy(self.level))
        for row in self.level:
            if row:
                row.pop()
        self.load_level_changes()
        self.render()

    def run_game(self):
        run_level(self.level)  # Call run_level on the current level

    def start_editor(self):
        self.camera.render_init()
        self.render()
        running = True
        while running:
            with self.term.cbreak():
                val = self.term.inkey(timeout=None)
                if CURSOR_MOVEMENT_CHANGE.get(val.name) == None and SCREEN_MOVEMENT_CHANGE.get(val) == None and CHANGE_OBJ.get(val) == None:
                    if val == "q":
                        Logger.write()
                        print(f"del list: {self.del_list}")
                        break
                    elif val == "p":
                        self.place_object()
                        
                    elif val == "r":
                        self.delete_object()

                    elif val == "/":
                        self.run_game()

                    elif val == "s":
                        self.save_level("levels/temp.level")

                    elif val == ".":
                        filename = input("Enter filename to load: ")
                        self.load_level(filename)

                    elif val == "c":
                        self.all_clear()

                    elif val == "u":
                        self.undo()

                    elif val == "+":
                        self.increase_height()

                    elif val == "-":
                        self.decrease_height()

                    elif val == ">":
                        self.increase_length()
                    elif val == "<":
                        self.decrease_length()

                        
                else:
                    if CURSOR_MOVEMENT_CHANGE.get(val.name) != None:
                        self.movecamera(val.name, True)
                    elif CHANGE_OBJ.get(val) != None:
                        self.update_cursor_obj(val)
                    else:
                        self.movecamera(val, False)
                self.render()
