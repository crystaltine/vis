import blessed

term = blessed.Terminal()

w = term.width
h = term.height


def clear():
    print(term.clear)

def update_screen(w, h, username):
    clear()

    print(term.clear + term.move_yx(int(h * 0.5)-1, int(w/2) - int(len("registered as " + username)/2)) + term.lime + "REGISTERED AS " + term.cyan + username + term.normal)

    print(term.move_yx(int(h * 0.5)+1, int(w/2) - int(len("[continue]")/2)) + term.black_on_lime + "[Continue]" + term.normal)

lw = w
lh = h

def show(username):
    w = term.width
    h = term.height
    
    lw = w
    lh = h
    update_screen(w, h, username)
    with term.cbreak():
        while True:
            w = term.width
            h = term.height
            key = term.inkey(timeout=0.01)
            if key: 
                code = key.code
                if code == 343:
                    break
            else:
                if lw != w or lh != h:
                    lw = w
                    lh = h
                    update_screen(w, h, username)