import blessed
term = blessed.Terminal()

import time


options = [
    "something",
    "something more",
    "something even more"
]


character_delay = 20

i = 0

print(term.clear)


def create_menu(options, foreground="black", background="white"):
    with term.hidden_cursor():
        m = max(len(i) for i in options)
        for n in range(m):
            letters = []
            for item in options:
                if n >= len(item):
                    letters.append(" ")
                else:
                    letters.append(item[n])
            
            for i, letter in enumerate(letters):
                print(term.move(i, n+2) + letter)
        #    print(term.move(n + 2, 0) + "\n".join(letters))
            time.sleep(1/1000 * character_delay)

        print(term.move(0, 0) + ">")

        select = 0
        with term.cbreak():
            val = ""
            while True:
                val = term.inkey()
                if val.code == 343: break
                if val.code == 259 and select > 0:
                    select -= 1
                    print(term.move(select + 1, 0) + " ")
                    print(term.move(select, 0) + ">")
                if val.code == 258 and select < len(options) - 1:
                    select += 1
                    print(term.move(select - 1, 0) + " ")
                    print(term.move(select, 0) + ">")
        print(term.move(select, 0) + " ")

        s = ""
        if foreground:
            s += foreground
        if foreground and background:
            s += "_"
        if background: 
            s += "on_" + background
        for n in range(len(options[select])):
            print(term.move(select, n + 2) + eval("term." + s) + options[select][n] + term.normal)
            time.sleep(1/1000 * character_delay)

        time.sleep(1.5)
        print(term.move(len(options), 0))

create_menu(options, foreground="black", background="mistyrose")