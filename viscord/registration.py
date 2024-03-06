import blessed

term = blessed.Terminal()

w = term.width
h = term.height

USER = ""
PASSWD = ""
CONFIRM = ""

print(term.clear + term.move_yx(int(h * 0.5)-3, int(w/2) - int(len("username")/2)) + "USERNAME")
print(term.move_yx(int(h * 0.5-2), int(w/2) - 2) + "____")
print(term.move_yx(int(h * 0.5-1), int(w/2) - int(len("password")/2)) + "PASSWORD")
print(term.move_yx(int(h * 0.5+0), int(w/2) - 2) + "____")
print(term.move_yx(int(h * 0.5+1), int(w/2) - int(len("confirm password")/2)) + "CONFIRM PASSWORD")
print(term.move_yx(int(h * 0.5+2), int(w/2) - 2) + "____")

y = 0

with term.cbreak():
    while True:
        key = term.inkey(timeout=0.01)
        if key: 
            if key in "qwertyuiopasdfghjklzxcvbnm":
                print(key)
            else:
                print(key.__dict__, repr(key))
        else:
            ...
            # TODO: resize code