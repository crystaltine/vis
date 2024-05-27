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

global username, password, color
username = ""
password = ""
color = ""

global error_show
error_show = False

global display_username, display_password, display_color
display_username = display_password = display_color = "..."

global FIELD_WIDTH
FIELD_WIDTH = int(term.width * 0.4 - 8) - 1
#               0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
ICON_CHOICES = "♠♣♥♦♫☺☍☇☾☼♁☿♀♃♄♅♆♇⚹*^$%!?⚀⚁⚂⚃⚄⚅"
ICON_CHOICES = sorted(ICON_CHOICES)

global icon_selection, icon_chunks
icon_selection = 0
icon_chunks = [ICON_CHOICES[i:i+FIELD_WIDTH] for i in range(0, len(ICON_CHOICES), FIELD_WIDTH)]


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
    x = center_text("Register")
    print(term.move(int(term.height*0.35) - 2, x) + term.color_rgb(*hex_to_rgb(COLORS.header)) + "Register", end="")

    print(term.move_yx(int(term.height*0.5) - 5, int(term.width * 0.3) + 4) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.bold("Username"), end="")
    print(term.move_yx(int(term.height*0.5) - 2, int(term.width * 0.3) + 4) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.bold("Password"), end="")
    print(term.move_yx(int(term.height*0.5) + 1, int(term.width * 0.3) + 4) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.bold("Color"), end="")
    print(term.move_yx(int(term.height*0.5) + 4, int(term.width * 0.3) + 4) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.bold("Symbol"), end="")
    
def draw_buttons():
    global selection
    x = center_text("Submit") - 3
    if selection == 4:
        color = COLORS.button_selected
    else:
        color = COLORS.button
    print(term.move(int(term.height*0.5)+7, x) + term.on_color_rgb(*hex_to_rgb(color)) + term.color_rgb(*hex_to_rgb(COLORS.text)) + term.bold(" " * 3 + "Submit" + " " * 3), end="")


def draw_fields():
    global FIELD_WIDTH
    f1 = f2 = f3 = f4 = COLORS.field
    global selection, cursor_pos
    if selection == 0:
        f1 = COLORS.field_highlighted
    elif selection == 1:
        f2 = COLORS.field_highlighted
    elif selection == 2:
        f3 = COLORS.field_highlighted
    elif selection == 3:
        f4 = COLORS.field_highlighted

    t1 = t2 = t3 = t4 = COLORS.unselected_text
    if selection == 0 or len(username) > 0:
        t1 = COLORS.text
    if selection == 1 or len(password) > 0:
        t2 = COLORS.text
    if selection == 2 or len(color) == 6:
        t3 = COLORS.text
    if selection == 3:
        t4 = COLORS.text

    display_username = username
    chunks = [display_username[i:i+FIELD_WIDTH-1] for i in range(0, len(display_username), FIELD_WIDTH-1)]
    
    if len(chunks) > 1:
        print(term.move_yx(int(term.height*0.5) - 4, int(term.width * 0.3) + 4 - 1) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + "<", end="")
    else:
        print(term.move_yx(int(term.height*0.5) - 4, int(term.width * 0.3) + 4 - 1) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + " ", end="")
    if len(username) == 0:
        if selection != 0: 
            display_username = "..."
        else:
            display_username = ""
    else:
        display_username = chunks[-1]
    print(term.move_yx(int(term.height*0.5) - 4, int(term.width * 0.3) + 4) + term.on_color_rgb(*hex_to_rgb(f1)) + term.color_rgb(*hex_to_rgb(t1)) + display_username + " " * (FIELD_WIDTH - len(display_username)), end="")
    if selection == 0:
        print(term.move_yx(int(term.height*0.5) - 4, int(term.width * 0.3) + 4 + (len(display_username) if username else 0)) + term.on_color_rgb(*hex_to_rgb(COLORS.cursor)) + " ", end="")
    
    display_password = password
    # chunk displayed passwd
    chunks = [display_password[i:i+FIELD_WIDTH-1] for i in range(0, len(display_password), FIELD_WIDTH-1)]
    if len(chunks) > 1:
        print(term.move_yx(int(term.height*0.5) - 1, int(term.width * 0.3) + 4 - 1) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + "<", end="")
    else:
        print(term.move_yx(int(term.height*0.5) - 1, int(term.width * 0.3) + 4 - 1) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + " ", end="")
    if len(password) == 0: 
        if selection != 1:
            display_password = "..."
        else:
            display_password = ""
    else:
        display_password = chunks[-1]
        if selection != 1:
            display_password = "*" * len(display_password) # :P
    print(term.move_yx(int(term.height*0.5) - 1, int(term.width * 0.3) + 4) + term.on_color_rgb(*hex_to_rgb(f2)) + term.color_rgb(*hex_to_rgb(t2)) + display_password + " " * (FIELD_WIDTH - len(display_password)), end="")
    if selection == 1:
        print(term.move_yx(int(term.height*0.5) - 1, int(term.width * 0.3) + 4 + (len(display_password) if password else 0)) + term.on_color_rgb(*hex_to_rgb(COLORS.cursor)) + " ", end="")
    

    display_color = "#" + color
    if len(color) == 0: 
        if selection != 2:    
            display_color = "#..."
        else:
            display_color = "#"
    highlight = f3
    text_color = t3

    if len(color) == 6:
        if selection == 2:
            highlight = display_color

            r,g,b = hex_to_rgb(display_color)
            if r * 0.299 + g * 0.587 + b * 0.114 > 186:
                text_color = "#000000"
            else:
                text_color = COLORS.text
        else:
            text_color = display_color

    real_display_color = display_color
    chunks = [display_color[i:i+FIELD_WIDTH-1] for i in range(0, len(display_color), FIELD_WIDTH-1)]
    if len(chunks) > 1:
        print(term.move_yx(int(term.height*0.5) + 2, int(term.width * 0.3) + 4 - 1) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + "<", end="")
    else:
        print(term.move_yx(int(term.height*0.5) + 2, int(term.width * 0.3) + 4 - 1) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + " ", end="")
    real_display_color = chunks[-1]
    print(term.move_yx(int(term.height*0.5) + 2, int(term.width * 0.3) + 4) + term.on_color_rgb(*hex_to_rgb(highlight)) + term.color_rgb(*hex_to_rgb(text_color)) + real_display_color + term.on_color_rgb(*hex_to_rgb(f3)) + " " * (FIELD_WIDTH - len(real_display_color)), end="")
    if selection == 2:
        print(term.move_yx(int(term.height*0.5) + 2, int(term.width * 0.3) + 4 + (len(real_display_color) if color else 1)) + term.on_color_rgb(*hex_to_rgb(COLORS.cursor)) + " ", end="")
    
    
    printed_icons = icon_chunks[icon_selection // FIELD_WIDTH]
    rel_cursor_pos = icon_selection % FIELD_WIDTH
    print(term.move_yx(int(term.height*0.5) + 5, int(term.width * 0.3) + 4) + term.on_color_rgb(*hex_to_rgb(f4)) + term.color_rgb(*hex_to_rgb(t4)) + "".join(printed_icons) + " " * (FIELD_WIDTH - len(printed_icons)), end="")
    
    if selection != 3:
        icon_selection_color = term.color_rgb(*hex_to_rgb(COLORS.text))
    else:
        icon_selection_color = term.cyan

    print(term.move_yx(int(term.height*0.5) + 5, int(term.width * 0.3) + 4 + rel_cursor_pos) + term.on_color_rgb(*hex_to_rgb(COLORS.cursor)) + icon_selection_color + printed_icons[rel_cursor_pos], end="")
    

    chunk_cursor = icon_selection // FIELD_WIDTH
    if chunk_cursor < len(icon_chunks) - 1:
        print(term.move_yx(int(term.height*0.5) + 5, int(term.width * 0.3) + 4 + FIELD_WIDTH) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + ">", end="")
    else:
        print(term.move_yx(int(term.height*0.5) + 5, int(term.width * 0.3) + 4 + FIELD_WIDTH) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + " ", end="")
    if chunk_cursor > 0:
        print(term.move_yx(int(term.height*0.5) + 5, int(term.width * 0.3) + 4 - 1) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + "<", end="")
    else:
        print(term.move_yx(int(term.height*0.5) + 5, int(term.width * 0.3) + 4 - 1) + term.on_color_rgb(*hex_to_rgb(COLORS.div)) + term.cyan + " ", end="")


def redraw_all():
    global FIELD_WIDTH, icon_chunks
    
    FIELD_WIDTH = int(term.width * 0.4 - 8) - 1
    icon_chunks = [ICON_CHOICES[i:i+FIELD_WIDTH] for i in range(0, len(ICON_CHOICES), FIELD_WIDTH)]

    draw_background()
    draw_menu()
    draw_all_text()
    draw_fields()
    draw_buttons()
    print("", end="", flush=True)

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

def main():
    global selection, cursor_pos, username, password, error_show, display_username, display_password, icon_selection, color
    redraw_all()
    cursor.hide()
    
    print("", end="", flush=True)

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

            if repr(val) == "KEY_ENTER" and selection == 4:
                # TODO
                ...
            if repr(val) in keyshortcuts.back_keys:
                selection = max(0, selection - 1)
                draw_fields()
                draw_buttons()
                print("", end="", flush=True)
            elif repr(val) in keyshortcuts.next_keys:
                selection = min(4, selection + 1)
                draw_fields()
                draw_buttons()
                print("", end="", flush=True)
            elif repr(val) == "KEY_LEFT":
                if selection == 3:
                    icon_selection = max(0, icon_selection - 1)
                    draw_fields()
            elif repr(val) == "KEY_RIGHT":
                if selection == 3:
                    icon_selection = min(len(ICON_CHOICES) - 1, icon_selection + 1)
                    draw_fields()
            elif repr(val) == "KEY_BACKSPACE":
                if selection == 0:
                    username = username[:-1]
                elif selection == 1:
                    password = password[:-1]
                elif selection == 2:
                    color = color[:-1]

                draw_fields()

                if error_show:
                    display_error(None)
                    error_show = False
                print("", end="", flush=True)
            elif val.is_sequence:
                pass
            else:
                if selection == 0:
                    username += val
                if selection == 1:
                    password += val
                if selection == 2:
                    if val in keyshortcuts.color_keys and len(color) < 6:
                        color += val
                draw_fields()
                if error_show:
                    display_error(None)
                    error_show = False
            print("", end="", flush=True)
            if term.width != sx or term.height != sy:
                redraw_all()
main()

main()