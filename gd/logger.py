from time import time
import os

class Logger:

    buffer = []
    _count = 0

    onscreen_history = []
    max_onscreen_len = 5

    def log(msg: str):
        Logger.buffer.append(str(msg))
        Logger._count += 1

    @staticmethod
    def log_on_screen(term, msg: str):
        """
        Actually prints a message to the terminal - always prints at top left corner.
        """
        
        Logger.onscreen_history.append(f"[LOG#{len(Logger.onscreen_history)+1}] {msg}")
        
        # always render newest messages at the bottom.
        # 5th most recent message starts from row0col0, 4th most starts from row1col0, etc.
        #if less than 5, then just print from row0col0 to rowNcol0
        
        for i in range(min(len(Logger.onscreen_history), Logger.max_onscreen_len)):
            print(term.move_xy(0, i) + Logger.onscreen_history[-i-1] + "\x1b[0m" + " "*(term.width-len(Logger.onscreen_history[-i-1])), end="")
            
    def write_old(dont_clear_buffer: bool = False):
        
        if len(Logger.buffer) > 0:
            
            # create log dir if nonexistent, prevents error
            if not os.path.exists((fp:=os.path.dirname(os.path.realpath(__file__)))+"/logs"):
                os.makedirs(fp+"/logs")

            with open(f"logs/{int(time())}.log", "w", encoding='utf-8') as log_f:
                log_f.writelines('\n'.join(Logger.buffer))
                log_f.close()
                print(f"\x1b[0mLogged {Logger._count} messages to logs/{int(time())}.log.")

                if not dont_clear_buffer:
                    Logger.buffer.clear()
        
        else:
            print(f"\x1b[0mLogger buffer is empty, did not write to file.")
            
    def write(dont_clear_buffer: bool = False):
        """ Writes logs to `latest.log`. Clears and rewrites every time so you dont have to dig through 10000 log files. """

        if len(Logger.buffer) > 0:
            with open(f"latest.log", "w", encoding='utf-8') as log_f:
                # first, write curr timestamp
                log_f.write(f">>> LOG TIMESTAMP {time()}\n\n")
                log_f.writelines('\n'.join(Logger.buffer))
                log_f.close()
                print(f"\x1b[0mLogged {Logger._count} messages to latest.log.")

                if not dont_clear_buffer:
                    Logger.buffer.clear()

        else:
            print(f"\x1b[0mLogger buffer is empty, did not write to file.")