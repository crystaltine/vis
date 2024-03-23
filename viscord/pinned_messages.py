import blessed 
#Creates Terminal Object + MessageUI object 
pinned_message_term = blessed.Terminal()
print(pinned_message_term.clear())

class PinnedMessageUI:
    #Terminal Height and Width 
    y = pinned_message_term.height 
    x = pinned_message_term.width 
    #Draw Box Function 
    def create_pinned_messages_box(box_height, box_width, box_x_pos, box_y_pos, title):
        #Top Border 
        print(pinned_message_term .move_yx(box_y_pos, box_x_pos) + pinned_message_term.red(pinned_message_term.bold("┌")) + 
            pinned_message_term.red(pinned_message_term.bold("─")) * (box_width - 2) + pinned_message_term.red(pinned_message_term.bold("┐")))
        #Left and Right Border 
        for i in range (1, box_height-1):
            print(pinned_message_term.move_yx(box_y_pos + i, box_x_pos) + pinned_message_term.red(pinned_message_term.bold("│")) + pinned_message_term.on_gray21(" " * (box_width - 2)) + 
                pinned_message_term.red(pinned_message_term.bold('│'))) 
        #Box Title 
        print(pinned_message_term.move_yx(box_y_pos - 18, box_x_pos + 30) + title)
        #Bottom Border 
        print(pinned_message_term.move_yx(box_y_pos + box_height - 1, box_x_pos) + pinned_message_term.red(pinned_message_term.bold("└")) + pinned_message_term.red(pinned_message_term.bold("─")) * 
              (box_width - 2) + pinned_message_term.red(pinned_message_term.bold('┘'))) 
    
        