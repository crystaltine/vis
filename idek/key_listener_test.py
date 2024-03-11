from blessed import Terminal
from pynput import keyboard

term = Terminal()

def on_press(key):
    if key == keyboard.Key.esc:
        return False 
    print(f"onpress: key: {key}")
    
def on_release(key):
    print(f"onrelease: key: {key}")

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keys