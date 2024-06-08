from editor.level_editor import LevelEditor
from logger import Logger
from draw_utils import cls
from cursor import hide, show
import traceback

fp = "./levels/official/stereo_madness.json"
editor = LevelEditor(fp)

def main():
    try:
        hide()
        editor.run_editor()
    except Exception as e:
        cls()
        Logger.log(f"EXCEPTION [test_level_editor/main]: {e}")
        print(traceback.format_exc())
        
    Logger.write()
    show()
    
if __name__ == "__main__":
    main()
