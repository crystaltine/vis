from editor.level_editor import LevelEditor
from logger import Logger
from draw_utils import cls
from cursor import hide, show
import traceback

fp = "./levels/created2.json"


def run_level_editor(path):
    editor = LevelEditor(path)
    try:
        hide()
        editor.run_editor()
    except Exception as e:
        cls()
        Logger.log(f"EXCEPTION [test_level_editor/main]: {e}")
        print(traceback.format_exc())
        
    Logger.write()
    show()
    
# if __name__ == "__main__":
#     main()
