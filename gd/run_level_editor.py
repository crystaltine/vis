from editor.level_editor import *

from logger import Logger
from draw_utils import cls


def run_editor(path):
    test = LevelEditor(path)
    test.run_editor()
   