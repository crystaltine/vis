import blessed
import cursor
import cursor

# initialize terminal
term = blessed.Terminal()

# initialize variables
w = term.width
h = term.height
USER = ""
PASSWD = ""
CONFIRM = ""
ERROR_MSG = ""
# position of focus I think
y = 0
lw = term.width
lh = term.height

BAD_USERNAME = BAD_PASSWD = BAD_CONF = False

cursor.hide()

# clears the terminal screen
# clears the terminal screen
def clear():
    print(term.clear)


# updates the screen with input fields and buttons
def update_screen(w, h, y): # honestly idk why either
    clear()
    
    
    print(term.clear + term.move_yx(int(h * 0.5)-3, int(w/2) - int(len("username")/2)) + "USERNAME")
    update_user(w, h, y == 0)

    print(term.move_yx(int(h * 0.5-1), int(w/2) - int(len("password")/2)) + "PASSWORD")
    update_passwd(w, h, y == 1)
    
    print(term.move_yx(int(h * 0.5+1), int(w/2) - int(len("confirm password")/2)) + "CONFIRM PASSWORD")
    update_confirm(w, h, y == 2)

    update_button(w, h, y == 3)
    update_back(w, h, y == 4)

    if ERROR_MSG:
        print(term.move_yx(-1, 0) + term.clear_eol + term.move_yx(h-1, int(w/2 - len(ERROR_MSG)/2)) + term.black_on_red + ERROR_MSG + term.normal)


# updates the username field
# updates the username field
def update_user(w, h, focused):
    if not USER:
        t = "____"
    else:
        t = USER
    if focused:
        if BAD_USERNAME:
            print(term.move_yx(int(h * 0.5) - 2, 0) + term.clear_eol + term.move_yx(int(h * 0.5-2), int(w/2 - len(t)/2)) + term.black_on_red + t + term.normal)
        else:
            print(term.move_yx(int(h * 0.5) - 2, 0) + term.clear_eol + term.move_yx(int(h * 0.5-2), int(w/2 - len(t)/2)) + term.black_on_cyan + t + term.normal)
    else:
        if BAD_USERNAME:
            print(term.move_yx(int(h * 0.5) - 2, 0) + term.clear_eol + term.move_yx(int(h * 0.5-2), int(w/2 - len(t)/2)) + term.red + t + term.normal)
        else:
            print(term.move_yx(int(h * 0.5) - 2, 0) + term.clear_eol + term.move_yx(int(h * 0.5-2), int(w/2 - len(t)/2)) + term.cyan + t + term.normal)

# updates the password field
# updates the password field
def update_passwd(w, h, focused):
    if not PASSWD:
        t = "____"
    else:
        t = "*" * len(PASSWD)
    if focused:
        if BAD_PASSWD:
            print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.black_on_red + t + term.normal)
        else:
            print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.black_on_cyan + t + term.normal)
    else:
        if BAD_PASSWD:
            print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.red + t + term.normal)
        else:
            print(term.move_yx(int(h * 0.5) - 0, 0) + term.clear_eol + term.move_yx(int(h * 0.5-0), int(w/2 - len(t)/2)) + term.cyan + t + term.normal)

# updates the confirm password field
# updates the confirm password field
def update_confirm(w, h, focused):
    if not CONFIRM:
        t = "____"
    else:
        t = "*" * len(CONFIRM)
    if focused:
        if BAD_CONF:
            print(term.move_yx(int(h * 0.5) +2, 0) + term.clear_eol + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)) + term.black_on_red + t + term.normal + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)))
        else:
            print(term.move_yx(int(h * 0.5) +2, 0) + term.clear_eol + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)) + term.black_on_cyan + t + term.normal + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)))
        
    else:
        if BAD_CONF:
            print(term.move_yx(int(h * 0.5) +2, 0) + term.clear_eol + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)) + term.red + t + term.normal)
        else:
            print(term.move_yx(int(h * 0.5) +2, 0) + term.clear_eol + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)) + term.cyan + t + term.normal)

# updates the register button
# updates the register button
def update_button(w, h, focused):
    t = "[Register]"
    if focused:
        print(term.move_yx(int(h * 0.5) +4, 0) + term.clear_eol + term.move_yx(int(h * 0.5+4), int(w/2 - len(t)/2)) + term.black_on_lime + t + term.normal + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)))
    else:
        print(term.move_yx(int(h * 0.5) +4, 0) + term.clear_eol + term.move_yx(int(h * 0.5+4), int(w/2 - len(t)/2)) + term.lime + t + term.normal)

def update_back(w, h, focused):
    t = "[Back]"
    if focused:
        print(term.move_yx(int(h * 0.5) +5, 0) + term.clear_eol + term.move_yx(int(h * 0.5+5), int(w/2 - len(t)/2)) + term.black_on_white + t + term.normal + term.move_yx(int(h * 0.5+2), int(w/2 - len(t)/2)))
    else:
        print(term.move_yx(int(h * 0.5) +5, 0) + term.clear_eol + term.move_yx(int(h * 0.5+5), int(w/2 - len(t)/2)) + term.white + t + term.normal)
    

# check if username already exists (placeholder implementation)
def check_username():
    # TODO: actually access db to check if username exists or not
    return True

# Initial screen update
# Initial screen update
update_screen(w, h, y)

# Main loop to handle user input
# Main loop to handle user input
with term.cbreak():
    while True:
        # handles in case of resizing probably 
        # handles in case of resizing probably 
        w = term.width
        h = term.height
        try:
            key = term.inkey(timeout=0.01)
        except KeyboardInterrupt:
            clear()
            cursor.show()
            exit()
        if key: 
            if key.lower() in r"`qwertyuiopasdfghjklzxcvbnm12345667890-=!@#$%^&*()_+[]{}":
                # handle alphanumeric input
                if y == 0:
                    USER += key.lower()
                    if BAD_USERNAME:
                        BAD_USERNAME = False
                        ERROR_MSG = ""
                        print(term.move_yx(h-2, 0) + term.clear_eol)
                    update_user(w, h, True)

                elif y == 1:
                    PASSWD += key
                    if BAD_PASSWD:
                        BAD_PASSWD = False
                        ERROR_MSG = ""
                        print(term.move_yx(h-2, 0) + term.clear_eol)
                    update_passwd(w, h, True)
                elif y == 2:
                    CONFIRM += key
                    if BAD_CONF:
                        BAD_CONF = False
                        ERROR_MSG = ""
                        print(term.move_yx(h-2, 0) + term.clear_eol)
                    update_confirm(w, h, True)

            else:
                #handles arrow keys and such
                #handles arrow keys and such
                code = key.code
                if (code in [258, 512] and y < 4) or (code == 343 and y < 3):
                    if y == 0:
                        update_user(w, h, False)
                        update_passwd(w, h, True)
                    if y == 1:
                        update_passwd(w, h, False)
                        update_confirm(w, h, True)
                    if y == 2:
                        update_confirm(w, h, False)
                        update_button(w, h, True)
                    if y == 3:
                        update_button(w, h, False)
                        update_back(w, h, True)
                    y += 1
                elif code in [259, 353] and y > 0:
                    if y == 4:
                        update_back(w, h, False)
                        update_button(w, h, True)
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

                elif code == 263:
                    if y == 0:
                        check = len(USER) > 0
                        USER = USER[:-1]
                        if BAD_USERNAME and check:
                            BAD_USERNAME = False
                            ERROR_MSG = ""
                            print(term.move_yx(h-2, 0) + term.clear_eol)
                        update_user(w, h, True)
                    elif y == 1:
                        PASSWD = PASSWD[:-1]
                        if BAD_PASSWD:
                            BAD_PASSWD = False
                            ERROR_MSG = ""
                            print(term.move_yx(h-2, 0) + term.clear_eol)
                        if BAD_CONF:
                            BAD_CONF = False
                            ERROR_MSG = ""
                            print(term.move_yx(h-2, 0) + term.clear_eol)
                            update_confirm(w, h, False)
                        update_passwd(w, h, True)
                    elif y == 2:
                        CONFIRM = CONFIRM[:-1]
                        if BAD_CONF:
                            BAD_CONF = False
                            ERROR_MSG = ""
                            print(term.move_yx(h-2, 0) + term.clear_eol)
                        if BAD_PASSWD:
                            BAD_PASSWD = False
                            ERROR_MSG = ""
                            print(term.move_yx(h-2, 0) + term.clear_eol)
                            update_passwd(w, h, False)
                        update_confirm(w, h, True)
                elif y == 4 and code == 343:
                    break
                elif code == 343 and y == 3:
                    # TODO prob implement other rules
                    # register button press
                    ERROR_MSG = ""
                    if not USER:
                        ERROR_MSG = "[Username cannot be blank.]"
                        BAD_USERNAME = True
                        update_user(w, h, False)
                    elif not check_username():
                        ERROR_MSG = "[User already exists.]"
                        BAD_USERNAME =  True
                        update_user(w, h, False)
                    elif not PASSWD:
                        ERROR_MSG = "[Password cannot be blank.]"
                        BAD_PASSWD = True
                        update_passwd(w, h, False)
                    elif PASSWD != CONFIRM:
                        ERROR_MSG = "[Passwords do not match.]"
                        BAD_CONF = True
                        update_confirm(w, h, False)
                    
                    if ERROR_MSG:
                        print(term.move_yx(h-2, 0) + term.clear_eol + term.move_yx(h-2, int(w/2 - len(ERROR_MSG)/2)) + term.black_on_red + ERROR_MSG + term.normal + "\a")
                    else:
                        import registered
                        registered.show(USER)
                        clear()
                        exit() # TODO: link up to main ui

        
                        
        # also resizing I think
        else:
            if lw != w or lh != h:
                lw = w
                lh = h
                update_screen(w, h, y)