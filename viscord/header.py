from blessed import Terminal

term = Terminal()

def draw_header():
    print(term.on_color_rgb(173, 216, 230), end='')

    with term.location(0, 0):
        print(term.clear_eol + term.color_rgb(255, 255, 255) + "Viscord", end="")
        quittext = "Ctrl+Q to Quit"
        with term.location(term.width - len(quittext), 0):
            print(term.color_rgb(252, 0, 0) + quittext)

    print(term.normal + term.on_color_rgb(100, 100, 100), end='')

    keybinds = [
        ("Servers", "Ctrl+S"),
        ("Chats", "Ctrl+C"),
        ("Messages", "Ctrl+M"),
        ("Settings", "Ctrl+H")
    ]
    keybind_str = '  '.join(f"{name} [{keybind}]" for name, keybind in keybinds)
    center_pos = (term.width - len(keybind_str)) // 2

    with term.location(center_pos, 1):
        print(term.white + keybind_str)

def clear_terminal():
    print(term.clear)

with term.cbreak():
    draw_header()
    val = ''
    while val.lower() != 'q':
        val = term.inkey()
    clear_terminal()
