import platform

def clear():
    if platform.system() == "Windows":
        import os
        os.system('cls')
    else:
        import os
        os.system('clear')

clear()