from menus.menu_handler import MenuHandler
from logger import Logger
import traceback
from cursor import hide, show
from draw_utils import cls

def main():
    MenuHandler.run() # if youre looking for code, start here

if __name__ == "__main__":
    try:
        hide()
        main()
        cls()        
    
    except Exception as e:
        Logger.log(f"[Main Thread/main2.py] Error: {traceback.format_exc()}")
        cls()
        print(f"\x1b[31m{traceback.format_exc()}\x1b[0m")
    
    show()        
    Logger.write()
        