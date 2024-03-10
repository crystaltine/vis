from blessed import Terminal
import time

term = Terminal()

def draw_settings_page(selected_mode, notifications_enabled):
    print(term.clear)

    heading = "Settings"
    heading_padding = (term.width - len(heading)) // 2
    print(term.move_yx(2, heading_padding) + term.bold(heading))

    mode_options = ["Light Mode", "Dark Mode"]
    mode_y = 6
    for i, mode in enumerate(mode_options):
        if selected_mode == i:
            print(term.move_yx(mode_y + i, 4) + term.reverse(mode))
        else:
            print(term.move_yx(mode_y + i, 4) + mode)

    notifications_text = "Notifications (Ctrl+N to Toggle): "
    notifications_status = "On" if notifications_enabled else "Off"
    notifications_y = 10
    print(term.move_yx(notifications_y, 4) + notifications_text + term.reverse(notifications_status))

    logout_text = "Logout (Ctrl+L)"
    logout_padding = (term.width - len(logout_text)) // 2
    logout_y = 16
    print(term.move_yx(logout_y, logout_padding) + term.reverse(logout_text))

selected_mode = 0 
notifications_enabled = True

with term.cbreak():
    draw_settings_page(selected_mode, notifications_enabled)
    while True:
        key = term.inkey()
        if key.name == "KEY_UP":
            selected_mode = (selected_mode - 1) % 2
        elif key.name == "KEY_DOWN":
            selected_mode = (selected_mode + 1) % 2
        elif key.lower() == "n":
            notifications_enabled = not notifications_enabled
        elif key.lower() == "l":
            break
