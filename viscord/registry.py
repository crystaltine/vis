REG_PATH = "SOFTWARE\\viscord\\settings"

# check if system is windows or linux
import platform

plat = platform.system()
import os

if plat != "Windows":
    if not os.path.exists(os.path.expanduser("~/.config/viscord")):
        os.makedirs(os.path.expanduser("~/.config/viscord"))

    REG_PATH = os.path.expanduser("~/.config/viscord")



import winreg
def set_reg(name, value):

    if plat != "Windows":
        with open(os.path.join(REG_PATH, name), "w") as f:
            f.write(value)
        return True
    else:
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, 
                                        winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

def get_reg(name):
    if plat != "Windows":
        try:
            with open(os.path.join(REG_PATH, name), "r") as f:
                return f.read()
        except FileNotFoundError:
            return None
    else:
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                        winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, name)
            winreg.CloseKey(registry_key)
            return value
        except WindowsError:
            return None
        
def del_reg(name):
    if plat != "Windows":
        try:
            os.remove(os.path.join(REG_PATH, name))
            return True
        except FileNotFoundError:
            return False
    else:
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                        winreg.KEY_WRITE)
            winreg.DeleteValue(registry_key, name)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False
        

