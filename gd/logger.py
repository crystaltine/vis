from time import time
import os

class Logger:

    buffer = []
    _count = 0

    def log(msg: str):
        Logger.buffer.append(msg)
        Logger._count += 1

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