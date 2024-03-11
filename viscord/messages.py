import blessed 
import os, sys 
import curses 
#Creates Terminal Object 
message_term = blessed.Terminal()
print(message_term.clear)

class MessageUI:
    #Terminal Height and Width 
    y = message_term.height 
    x = message_term.width 
    #Draw Box Method
    def draw_a_box(box_height, box_width, box_x, box_y):
        print(message_term.move_yx(box_y, box_x) + message_term.bold("┌") + message_term.bold("─") * (box_width - 2) + message_term.bold('┐'))
        for i in range (1, box_height-1):
            print(message_term.move_yx(box_y + i, box_x) + message_term.bold("│") + " " * (box_width - 2) + message_term.bold('│'))
        print(message_term.move_yx(box_y + box_height - 1, box_x) + message_term.bold("└") + message_term.bold("─") * (box_width - 2) + message_term.bold('┘'))

    draw_a_box(25, 100, 30, 20)
    print(message_term.purple(str(y) + str(x)))

"""
counter = 0 
    b = True
    while b:
        counter += 1
        print(message_term.on_gray21)
        if counter == 30:
            b = False 
"""