from pynput import keyboard
from time import sleep
import blessed

term = blessed.Terminal()

def on_press(key):

    if type(key) == keyboard.KeyCode:
        print(f"Keycode: {key}")
        return

    key_char = getattr(key, "char", None)
    print(f'keydown: {key_char or key}')
    if key.ctrl: print(f"KEYDOWN: ctrl ({key.ctrl})")
    if key.alt: print(f"KEYDOWN: alt ({key.alt})")
    if key.shift: print(f"KEYDOWN: shift ({key.shift})")

def on_release(key):
    print(f'{key} released, type={type(key)}')
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
#with keyboard.Listener(
#        on_press=on_press,
#        on_release=on_release) as listener:
#    listener.join()

for i in range(5, term.height-5):
    with term.location(10, i):
        print(f"\033[48;2;63;129;189m" + " "*(term.width-20), end="")
        
with term.location(20, 20):
    a = input("\033[38;2;255;255;0m\033[48;2;144;144;144m")

print(a + " < u typed this")