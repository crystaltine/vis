import win32gui
import os

os.system('title testthingy')
print(win32gui.GetWindowText(win32gui.GetForegroundWindow())) # prints 'testthingy'