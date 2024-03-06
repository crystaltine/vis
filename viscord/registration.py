import blessed

term = blessed.Terminal()

w = term.width
h = term.height

USER = ""
PASSWD = ""
CONFIRM = ""


import cursor
cursor.hide()

def clear():
    print(term.clear)

def update_screen(w, h, y): # honestly idk why either
    clear()
    print(term.clear + term.move_yx(int(h * 0.5)-3, int(w/2) - int(len("username")/2)) + "USERNAME")
    update_user(w, h, y == 0)

    print(term.move_yx(int(h * 0.5-1), int(w/2) - int(len("password")/2)) + "PASSWORD")
    update_passwd(w, h, y == 1)
    
    print(term.move_yx(int(h * 0.5+1), int(w/2) - int(len("confirm password")/2)) + "CONFIRM PASSWORD")
    update_confirm(w, h, y == 2)

    update_button(w, h, y == 3)

y = 0

lw = term.width
lh = term.height

def update_user(w, h, focused):
    if not USER:
        t = "____"
    else:
        t = USER
    if focused:
        print(term.move_yx(int(h * 0.5) - 2, 0) + term.clear_eol + term.move_yx(int(h * 0.5-2), int(w/2 - len(t)/2)) + term.black_on_cyan + t + term.normal)
    else:
        print(term.move_yx(int(h * 0.5) - 2, 0) + term.clear_eol + term.move_yx(int(h * 0.5-2), int(w/2 - len(t)/2)) + term.cyan + t + term.normal)

def update_passwd(w, h, focused):
    if not PASSWD:
        t = "____"
    else:
        t = PASSWD
    if focused:
        print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.black_on_cyan + t + term.normal)
    else:
        print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.cyan + t + term.normal)

def update_confirm(w, h, focused):
    if not CONFIRM:
        t = "____"
    else:
        t = CONFIRM
    if focused:
        print(term.move_yx(int(h * 0.5) +2, 0) + term.clear_eol + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)) + term.black_on_cyan + t + term.normal + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)))
    else:
        print(term.move_yx(int(h * 0.5) +2, 0) + term.clear_eol + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)) + term.cyan + t + term.normal)

def update_button(w, h, focused):
    t = "[Register]"
    if focused:
        print(term.move_yx(int(h * 0.5) +4, 0) + term.clear_eol + term.move_yx(int(h * 0.5+4), int(w/2 - len(t)/2)) + term.black_on_lime + t + term.normal + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)))
    else:
        print(term.move_yx(int(h * 0.5) +4, 0) + term.clear_eol + term.move_yx(int(h * 0.5+4), int(w/2 - len(t)/2)) + term.normal + t + term.normal)


update_screen(w, h, y)


with term.cbreak():
    while True:
        w = term.width
        h = term.height
        key = term.inkey(timeout=0.01)
        if key: 
            if key.lower() in r"qwertyuiopasdfghjklzxcvbnm12345667890-=!@#$%^&*()_+[]{}":
                if y == 0:
                    USER += key.lower()
                    update_user(w, h, True)
                elif y == 1:
                    PASSWD += key
                    update_passwd(w, h, True)
                elif y == 2:
                    CONFIRM += key
                    update_confirm(w, h, True)

            else:
                code = key.code
                if code == 258 and y < 3:
                    if y == 0:
                        update_user(w, h, False)
                        update_passwd(w, h, True)
                    if y == 1:
                        update_passwd(w, h, False)
                        update_confirm(w, h, True)
                    if y == 2:
                        update_confirm(w, h, False)
                        update_button(w, h, True)
                    y += 1
                if code == 259 and y > 0:
                    if y == 2:
                        update_confirm(w, h, False)
                        update_passwd(w, h, True)
                    if y == 1:
                        update_passwd(w, h, False)
                        update_user(w, h, True)
                    if y == 3:
                        update_button(w, h, False)
                        update_confirm(w, h, True)
                    y -= 1

                if code == 263:
                    if y == 0:
                        USER = USER[:-1]
                        update_user(w, h, True)
                    elif y == 1:
                        PASSWD = PASSWD[:-1]
                        update_passwd(w, h, True)
                    elif y == 2:
                        CONFIRM = CONFIRM[:-1]
                        update_confirm(w, h, True)

        else:
            if lw != w or lh != h:
                lw = w
                lh = h
                update_screen(w, h, y)