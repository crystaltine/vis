import blessed 
import textwrap
from messages import MessageUI
#Creates Terminal Object + MessageUI object 
pinned_message_term = blessed.Terminal()
print(pinned_message_term.clear())
messages = MessageUI() 

class PinnedMessageUI:
    #Terminal Height and Width 
    z = None 
    y = pinned_message_term.height 
    x = pinned_message_term.width 
    #Draw Box Function 
    def draw_a_box(box_height, box_width, box_x_pos, box_y_pos, title):
        #Top Border 
        print(pinned_message_term .move_yx(box_y_pos, box_x_pos) + pinned_message_term.red(pinned_message_term.bold("┌")) + 
            pinned_message_term.red(pinned_message_term.bold("─")) * (box_width - 2) + pinned_message_term.red(pinned_message_term.bold("┐")))
        #Left and Right Border 
        for i in range (1, box_height-1):
            print(pinned_message_term.move_yx(box_y_pos + i, box_x_pos) + pinned_message_term.red(pinned_message_term.bold("│")) + pinned_message_term.on_gray21(" " * (box_width - 2)) + 
                pinned_message_term.red(pinned_message_term.bold('│'))) 
        #Box Title 
        print(pinned_message_term.move_yx(box_y_pos - 18, box_x_pos + 32) + title)
        #Bottom Border 
        print(pinned_message_term.move_yx(box_y_pos + box_height - 1, box_x_pos) + pinned_message_term.red(pinned_message_term.bold("└")) + pinned_message_term.red(pinned_message_term.bold("─")) * 
              (box_width - 2) + pinned_message_term.red(pinned_message_term.bold('┘'))) 
    #Draw the messages box 
    while True: 
        with pinned_message_term.cbreak(): 
            open_key_bind = 'p'
            close_key_bind = 'c'
            if pinned_message_term.inkey() == open_key_bind:
                box = draw_a_box(25, 75, 30, 20, pinned_message_term.purple_on_gray21(pinned_message_term.bold("Pinned Messages"))) 
            if pinned_message_term.inkey() == close_key_bind:
                print(pinned_message_term.clear()) 
                print(messages.draw_a_box())
                
        