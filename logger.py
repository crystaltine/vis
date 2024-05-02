from time import time
import os
from globalvars import Globals

class Logger:

    buffer = []
    _count = 0
    
    onscreen_history = []
    max_onscreen_len = 5

    def log(msg: str):
        Logger.buffer.append(msg)
        Logger._count += 1

    def log_on_screen(msg: str):
        """
        Actually prints a message to the terminal - always prints at top left corner.
        """
        
        Logger.onscreen_history.append(msg)
        
        # always render newest messages at the bottom.
        # 5th most recent message starts from row0col0, 4th most starts from row1col0, etc.
        #if less than 5, then just print from row0col0 to rowNcol0
        
        for i in range(min(len(Logger.onscreen_history), Logger.max_onscreen_len)):
            with Globals.__vis_document__.term.hidden_cursor():
                print(Globals.__vis_document__.term.move_xy(0, i) + f"[INFO] " + Logger.onscreen_history[-i-1], end="")
        
        #with Globals.__vis_document__.term.hidden_cursor():
        #    print(Globals.__vis_document__.term.move_xy(0, 0) + msg, end="")

    def write(dont_clear_buffer: bool = False):
        
        if len(Logger.buffer) > 0:
            
            # create log dir if nonexistent, prevents error
            if not os.path.exists((fp:=os.path.dirname(os.path.realpath(__file__)))+"/logs"):
                os.makedirs(fp+"/logs")

            with open(f"logs/{int(time())}.log", "w") as log_f:
                log_f.writelines('\n'.join(Logger.buffer))
                log_f.close()
                print(f"Logged {Logger._count} messages to logs/{int(time())}.log.")

                if not dont_clear_buffer:
                    Logger.buffer.clear()