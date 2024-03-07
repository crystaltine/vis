import blessed

term = blessed.Terminal()

w = term.width
h = term.height

USER = ""
PASSWD = ""

ERROR_MSG = ""
BAD_PASSWORD = False

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
    

    update_button(w, h, y == 2)

    if ERROR_MSG:
        print(term.move_yx(y-1, 0) + term.clear_eol + term.move_yx(h-2, int(w/2 - len(ERROR_MSG)/2)) + term.black_on_red + ERROR_MSG + term.normal)

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
        t = "*" * len(PASSWD)
    if focused:
        if BAD_PASSWORD:
            print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.black_on_red + t + term.normal)
        else:
            print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.black_on_cyan + t + term.normal)
    else:
        if BAD_PASSWORD:
            print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.red + t + term.normal)
        else:
            print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.cyan + t + term.normal)

def update_button(w, h, focused):
    t = "[Log In]"
    if focused:
        print(term.move_yx(int(h * 0.5) +4, 0) + term.clear_eol + term.move_yx(int(h * 0.5+3), int(w/2 - len(t)/2)) + term.black_on_lime + t + term.normal + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)))
    else:
        print(term.move_yx(int(h * 0.5) +4, 0) + term.clear_eol + term.move_yx(int(h * 0.5+3), int(w/2 - len(t)/2)) + term.lime + t + term.normal)

def check_creds(u, p):
    # TODO: actually access db to check if username exists or not
    import random
    return random.choice([False, True]) # DELETE AFTER DONE

update_screen(w, h, y)

with term.cbreak():
    while True:
        w = term.width
        h = term.height
        try:
            key = term.inkey(timeout=0.01)
        except KeyboardInterrupt:
            clear()
            exit()
        if key: 
            if key.lower() in r"qwertyuiopasdfghjklzxcvbnm1234567890-=!@#$%^&*()_+[]{}":
                if y == 0:
                    USER += key.lower()
                    if BAD_PASSWORD and len(PASSWD) > 0:
                        BAD_PASSWORD = False
                        ERROR_MSG = ""
                        update_passwd(w, h, False)
                        print(term.move_yx(h-2, 0) + term.clear_eol)
                    update_user(w, h, True)
                elif y == 1:
                    PASSWD += key
                    if BAD_PASSWORD:
                        BAD_PASSWORD = False
                        ERROR_MSG = ""
                        print(term.move_yx(h-2, 0) + term.clear_eol)
                    update_passwd(w, h, True)

            else:
                code = key.code
                if code in [258, 512, 343] and y < 2:
                    if y == 0:
                        update_user(w, h, False)
                        update_passwd(w, h, True)
                    if y == 1:
                        update_passwd(w, h, False)
                        update_button(w, h, True)
                    y += 1
                elif code in [259, 353] and y > 0:
                    if y == 2:
                        update_button(w, h, False)
                        update_passwd(w, h, True)
                    if y == 1:
                        update_passwd(w, h, False)
                        update_user(w, h, True)
                    y -= 1

                elif code == 263:
                    if y == 0:
                        USER = USER[:-1]
                        if BAD_PASSWORD:
                            BAD_PASSWORD = False
                            ERROR_MSG = ""
                            update_passwd(w, h, False)
                            print(term.move_yx(h-2, 0) + term.clear_eol)

                        update_user(w, h, True)
                    elif y == 1:
                        check = len(PASSWD) > 0
                        PASSWD = PASSWD[:-1]
                        if BAD_PASSWORD and check:
                            BAD_PASSWORD = False
                            ERROR_MSG = ""
                            print(term.move_yx(h-2, 0) + term.clear_eol)
                        update_passwd(w, h, True)

                elif code == 343 and y == 2:
                    ERROR_MSG = ""
                    if not USER:
                        ERROR_MSG = "[Username cannot be blank.]"
                    elif not PASSWD:
                        ERROR_MSG = "[Password cannot be blank.]"
                        BAD_PASSWORD = True
                        update_passwd(w, h, False)
                    elif not check_creds(USER, PASSWD):
                        ERROR_MSG = "[Invalid credentials]"
                        BAD_PASSWORD = True
                        update_passwd(w, h, False)
                    else:
                        # TODO: remove later
                        ERROR_MSG = "[Correct credentials, remove later]"

                    if ERROR_MSG:
                        print(term.move_yx(h-2, 0) + term.clear_eol + term.move_yx(h-2, int(w/2 - len(ERROR_MSG)/2)) + term.black_on_red + ERROR_MSG + term.normal + "\a")
                    else:
                        ...
                        # TODO: later

        else:
            if lw != w or lh != h:
                lw = w
                lh = h
                update_screen(w, h, y)