from time import time

class Logger:

    buffer = []
    _count = 0

    def log(msg: str):
        Logger.buffer.append(msg)
        Logger._count += 1

    def write(dont_clear_buffer: bool = False):
        with open(f"logs/{int(time())}.log", "w") as log_f:
            log_f.writelines('\n'.join(Logger.buffer))
            log_f.close()

            if not dont_clear_buffer:
                Logger.buffer.clear()