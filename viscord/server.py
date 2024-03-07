import blessed

term = blessed.Terminal()

NUM_SERVERS = 5
LIST_SERVERS = ["Hi", "pizza pizza", "asdf", "sadfasf", "monke monke"]
SCREEN_SIZE = [140, 43]

def enter_in(): #enter into the next leverl (ex: server -> chat)
    print(f"{levels[cur_level]}")
def backout(): #backout of most recent level (ex: chat -> server)
    print(f"{levels[cur_level]}")
def update():
    term.clear()
    print(f"{term.home}{term.black_on_skyblue}{term.clear}")
    for x in range(len(LIST_SERVERS)):
        if x == hovering:
            print(term.on_orangered + f"{LIST_SERVERS[x]}" + term.black_on_skyblue)
        else:
            print(f"{LIST_SERVERS[x]}")


hovering = 0 #which server/chat the user is hovering over
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
                    enter_in()
                if val.code == 361 and cur_level > 0:
                    cur_level -= 1
                    backout()
            if val.code in [258, 259]: #checks if keypress is and up or down arrow
                if val.code == 258 and hovering < NUM_SERVERS:
                    hovering += 1
                elif val.code == 259 and hovering > 0:
                    hovering -= 1
            
    print(f'bye!{term.normal}')
