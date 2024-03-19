import blessed

term = blessed.Terminal()

NUM_SERVERS = 3
LIST_SERVERS = ["Hi", "pizza pizza", "asdf"]
LIST_CHATS = {"Hi":["hello", "bye"], "pizza pizza":["pep", "chz"], "asdf":["qwerty", "zxcv"]}
WIDTH = 20
HEIGHT = 5


def enter_in(): #enter into the next leverl (ex: server -> chat)
    print(f"{levels[cur_level]}")
def backout(): #backout of most recent level (ex: chat -> server)
    print(f"{levels[cur_level]}")
def update_server_box():
    print("┌" + "─" * (WIDTH - 2) + "┐")
    for x in range(HEIGHT):
        if x < NUM_SERVERS:
            if cur_server == None:
                if x == hovering:
                    print(term.black_on_webgreen + "│" + f"{LIST_SERVERS[x]}".center(WIDTH - 2) + "│" + term.webgreen_on_black)
                else:
                    print("│" + f"{LIST_SERVERS[x]}".center(WIDTH - 2) + "│")
            else:
                if x == LIST_SERVERS.index(cur_server):
                    print(term.black_on_webgreen + "│" + f"{LIST_SERVERS[x]}".center(WIDTH - 2) + "│" + term.webgreen_on_black)
                else:
                    print("│" + f"{LIST_SERVERS[x]}".center(WIDTH - 2) + "│")
        else:
            for _ in range((HEIGHT - 2) // 2):
                print("│" + " " * (WIDTH - 2) + "│")
    print("└" + "─" * (WIDTH - 2) + "┘")

def update_chat_box():
    if cur_level == 1:
        print(term.move_yx(1, WIDTH) + "┌" + "─" * (WIDTH - 2) + "┐")
        for x in range(HEIGHT):
            if x < len(LIST_CHATS[cur_server]):
                if x == hovering:
                    print(term.move_right(WIDTH) + "│" + term.black_on_webgreen + f"{LIST_CHATS[cur_server][x]}".center(WIDTH - 2) + term.webgreen_on_black + "│")
                else:
                    print(term.move_right(WIDTH) + "│" + f"{LIST_CHATS[cur_server][x]}".center(WIDTH - 2) + "│")
            else:
                for _ in range((HEIGHT - 2) // 2):
                    print(term.move_right(WIDTH) + "│" + " " * (WIDTH - 2) + "│")
        print(term.move_right(WIDTH) + "└" + "─" * (WIDTH - 2) + "┘")
def update():
    term.clear()
    print(f"{term.home}{term.webgreen_on_black}{term.clear}")
    update_server_box()
    update_chat_box()

hovering = 0 #which server/chat the user is hovering over
cur_server = None
cur_level = 0 #server level
levels = ["server", "chats", "messages"]

with term.cbreak():
    val = ''
    while val.lower() != 'q':
        update()
        val = term.inkey(timeout=3)
        if val.is_sequence:
            if val.code in [343, 361]: #checks if keypress is enter or escape
                if val.code == 343 and cur_level < 2:
                    cur_level += 1
                    cur_server = LIST_SERVERS[hovering]
                    hovering = 0
                    enter_in()
                elif val.code == 361 and cur_level > 0:
                    cur_level -= 1
                    cur_server = None
                    hovering = 0
                    backout()
            if val.code in [258, 259]: #checks if keypress is and up or down arrow
                if val.code == 258 and hovering < NUM_SERVERS - 1:
                    hovering += 1
                elif val.code == 259 and hovering > 0:
                    hovering -= 1
            
    print(f'bye!{term.normal}')
