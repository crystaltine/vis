import blessed 
import os, sys 
import curses 
#Creates Terminal Object 
message_term = blessed.Terminal()
print(message_term.clear)

class MessageUI:
    #Terminal Height 
    y = message_term.height 
    x = message_term.width 
    #Box height,width,top,left
    box_height = 40
    box_width = 100
    box_x = 5
    box_y = 10 
    #Draw Box 
    print(message_term.move_yx())
    #for i in box_height: 
    print(message_term.move_yx())
    
    #print(message_term.purple(str(y)))

"""
counter = 0 
    b = True
    while b:
        counter += 1
        print(message_term.on_gray21)
        if counter == 30:
            b = False 
"""