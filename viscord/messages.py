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
    #Draw Box Function 
    def draw_a_box(box_height, box_width, box_x_pos, box_y_pos, title):
        #Top Border 
        print(message_term.move_yx(box_y_pos, box_x_pos) + message_term.blue(message_term.bold("┌")) + 
            message_term.blue(message_term.bold("─")) * (box_width - 2) + message_term.blue(message_term.bold("┐")))
        #Left and Right Border 
        for i in range (1, box_height-1):
            print(message_term.move_yx(box_y_pos + i, box_x_pos) + message_term.blue(message_term.bold("│")) + message_term.on_gray21(" " * (box_width - 2)) + 
                message_term.blue(message_term.bold('│'))) 
        #Box Title 
        print(message_term.move_yx(box_y_pos - 17, box_x_pos + 44) + title)
        #Bottom Border 
        print(message_term.move_yx(box_y_pos + box_height - 1, box_x_pos) + message_term.blue(message_term.bold("└")) + message_term.blue(message_term.bold("─")) * 
              (box_width - 2) + message_term.blue(message_term.bold('┘'))) 
    #Draw the messages box 
    box = draw_a_box(25, 100, 30, 20, message_term.green_on_gray21(message_term.bold("Viscord Chat"))) 
    
    