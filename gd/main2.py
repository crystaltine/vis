from menus.menu_handler import MenuHandler
from logger import Logger
import traceback
from cursor import hide, show
from draw_utils import cls

def main():
    MenuHandler.run()

if __name__ == "__main__":
    try:
        hide()
        test = main()
        Logger.log(f"[Main Thread/main2.py] Test: {test}")
            
    except Exception as e:
        Logger.log(f"[Main Thread/main2.py] Error: {traceback.format_exc()}")
        print(f"\x1b[31m{traceback.format_exc()}\x1b[0m")
    
    cls()
    show()        
    Logger.write()
        