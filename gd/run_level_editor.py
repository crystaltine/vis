from level_editor import LevelEditor
from logger import Logger
from draw_utils import cls



test = LevelEditor()

def run_editor():

    try:
        test.start_editor()
    except Exception as e:
        cls()
        Logger.log(f"EXCEPTION [user_settings/main]: {e}")
        Logger.write()
        print(f"\x1b[31mgd fatal: an error occurred, \x1b[33m{e}\x1b[0m")
        exit()