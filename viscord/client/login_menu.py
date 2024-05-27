import uuid
import blessed
term = blessed.Terminal()
import COLORS
import cursor
import keyshortcuts
import requests
import config
import registry
import sys

global selection
selection = 0
selected = None

global cursor_pos
cursor_pos = 0

global username, password
username = ""
password = ""

global error_show
error_show = False

global display_username, display_password
display_username = display_password = "..."

FIELD_WIDTH = int(term.width * 0.4 - 8) - 1


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def draw_background():
    print(term.home + term.clear, end=" ")
    for y in range(term.height):
        print(term.move(y, 0) + term.on_color_rgb(*hex_to_rgb(COLORS.background)) + ' ' * term.width, end="")


def draw_menu():
    tlx = int(term.width * 0.3)
    tly = int(term.height * 0.2)

    for y in range(tly, tly + int(term.height * 0.6)):
        print(term.move(y, tlx) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + ' ' * int(term.width * 0.4), end="")


def center_text(text):
    return int(term.width / 2 - len(text) / 2)

def draw_all_text():
    x = center_text("Log In")
    print(term.move(int(term.height*0.35) - 2, x) + term.color_rgb(*hex_to_rgb(COLORS.header)) + "Log In", end="")

    print(term.move_yx(int(term.height*0.5) - 4, int(term.width * 0.3) + 4) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.bold("Username"), end="")
    print(term.move_yx(int(term.height*0.5), int(term.width * 0.3) + 4) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.bold("Password"), end="")
    

def draw_fields():
    global selection, cursor_pos
    if selection == 0:
        f1 = COLORS.field_highlighted
        f2 = COLORS.field
    elif selection == 1:
        f1 = COLORS.field
        f2 = COLORS.field_highlighted
    else:
        f1 = COLORS.field
        f2 = COLORS.field

    if len(username) == 0:
        t1 = COLORS.unselected_text
    else:
        t1 = COLORS.text
    
    if len(password) == 0:
        t2 = COLORS.unselected_text
    else:
        t2 = COLORS.text



    print(term.move_yx(int(term.height*0.5) - 3, int(term.width * 0.3) + 4) + term.on_color_rgb(*hex_to_rgb(f1)) + " " * int(term.width * 0.4 - 8), end="")
    print(term.move_yx(int(term.height*0.5) + 1, int(term.width * 0.3) + 4) + term.on_color_rgb(*hex_to_rgb(f2)) + " " * int(term.width * 0.4 - 8), end="")

    global display_username, display_password
    print(term.move_yx(int(term.height*0.5) - 3, int(term.width * 0.3) + 4) + term.color_rgb(*hex_to_rgb(t1)) + term.on_color_rgb(*hex_to_rgb(f1)) + display_username, end="")
    print(term.move_yx(int(term.height*0.5) + 1, int(term.width * 0.3) + 4) + term.color_rgb(*hex_to_rgb(t2)) + term.on_color_rgb(*hex_to_rgb(f2)) + display_password, end="")

    if selection < 2:
        if selection == 0:
            y = int(term.height*0.5) - 3
            cursor_pos = len(username)
        elif selection == 1:
            y = int(term.height*0.5) + 1
            cursor_pos = len(password)
        
        print(term.move_yx(y, int(term.width * 0.3) + 4 + min(cursor_pos, FIELD_WIDTH)) + term.on_color_rgb(*hex_to_rgb(COLORS.cursor)) + " ", end="")


def draw_buttons():
    global selection
    x = center_text("Submit") - 3
    if selection == 2:
        color = COLORS.button_selected
    else:
        color = COLORS.button
    print(term.move(int(term.height*0.65), x) + term.on_color_rgb(*hex_to_rgb(color)) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.bold(" " * 3 + "Submit" + " " * 3), end="")

def display_error(msg):
    if not msg:
        print(term.move(int(term.height*0.65) + 2, int(term.width * 0.3)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + " " * int(term.width * 0.4), end="")
    else:
        print(term.move(int(term.height*0.65) + 2, center_text(msg)) + term.color_rgb(*hex_to_rgb(COLORS.error)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + msg, end="")

def display_success(msg):
    display_error(None)
    if not msg:
        print(term.move(int(term.height*0.65) + 2, int(term.width * 0.3)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + " " * int(term.width * 0.4), end="")
    else:
        print(term.move(int(term.height*0.65) + 2, center_text(msg)) + term.color_rgb(*hex_to_rgb(COLORS.success)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + msg, end="", flush=True)
        sys.stdout.flush()

def handle_submit():
    global error_show, username, password
    if len(username) == 0 or len(password) == 0:
        msg = ("Username" if len(username) == 0 else "Password") + " missing"
        display_error(msg)
        error_show = True
        return False
    try:
        resp = requests.post(f"https://{config.HOST}:{config.PORT}/api/login", json={"user": username, "password": password, "sys_uuid": str(uuid.getnode())})
    except Exception as e:
        display_error("Server error")
        error_show = True
        return False
    if resp.status_code == 200:
        
        display_success("Logged in as " + resp.json()["username"] + ", loading...")
        registry.set_reg("cache", resp.json()["cache"])
        handle_success(resp.json()["token"])
        return True
    elif resp.status_code == 403:
        display_error("Invalid credentials")
        error_show = True
        return False
    elif resp.status_code == 500:
        display_error("Server error: " + resp.json()["message"])
        error_show = True
        return False

def redraw_all():
    print(term.clear())
    draw_background()
    draw_menu()
    draw_all_text()
    draw_fields()
    draw_buttons()  
    print("")

def handle_success(token):
    import server_select
    server_select.main(token)

def main():
    
    cursor.hide()
    if len(sys.argv) > 1 and sys.argv[1] == "kill":
        registry.del_reg("cache")
    global username, password, display_username, display_password, selection, error_show

    if registry.get_reg("cache"):
        cache = registry.get_reg("cache")
        sys_uuid = str(uuid.getnode())
        try:
            resp = requests.post(f"https://{config.HOST}:{config.PORT}/api/login/bypass", json={"cache": cache, "sys_uuid": sys_uuid})
            if resp.status_code == 200:
                handle_success(resp.json()["token"])
                sys.exit(0)
            else:
                pass
        except Exception as e:
            raise

    redraw_all()
    
    

    with term.cbreak():
        val = ""
        while True:
            sx = term.width
            sy = term.height
            val = term.inkey(timeout=0.01)
            if not val:
                if term.width != sx or term.height != sy:
                    redraw_all()
                continue

            if repr(val) == "KEY_ENTER" and selection == 2:
                ret = handle_submit()
                if ret:
                    break
            if repr(val) in keyshortcuts.back_keys:
                selection = max(0, selection - 1)
                draw_fields()
                draw_buttons()
                print("")
            elif repr(val) in keyshortcuts.next_keys:
                selection = min(2, selection + 1)
                draw_fields()
                draw_buttons()
                print("")
            elif repr(val) == "KEY_BACKSPACE":
                global display_username, display_password
                if selection == 0:
                    username = username[:-1]
                    display_username = username[-FIELD_WIDTH:]
                    if len(username) == 0:
                        display_username = "..."
                else:
                    password = password[:-1]
                    display_password = "*" * min(len(password), FIELD_WIDTH)
                    if len(password) == 0:
                        display_password = "..."
                draw_fields()
                if error_show:
                    display_error(None)
                    error_show = False
                print("")
            elif val.is_sequence:
                pass
            else:
                if selection == 0:
                    if len(username) == 0:
                        display_username = ""
                    
                    username += val
                    display_username = username[-FIELD_WIDTH:]
                else:
                    if len(password) == 0:
                        display_password = ""
                    password += val
                    display_password = "*" * min(len(password), FIELD_WIDTH)
                draw_fields()
                if error_show:
                    display_error(None)
                    error_show = False
            print("")
            if term.width != sx or term.height != sy:
                redraw_all()
main()