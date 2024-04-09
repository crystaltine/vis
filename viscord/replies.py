import blessed 
from messages import MessageUI
#Creates Terminal Object + repliesUI object 
replies = blessed.Terminal()
print(replies.clear())

class Replies:
    #Terminal Height and Width 
    y = replies.height 
    x = replies.width 
    #Draw Box Function 
    def create_replies_box(box_height, box_width, box_x_pos, box_y_pos, title, mode):
        #Top Border 
        print(replies .move_yx(box_y_pos, box_x_pos) + replies.green(replies.bold("┌")) + 
            replies.green(replies.bold("─")) * (box_width - 2) + replies.green(replies.bold("┐")))
        #Left and Right Border 
        for i in range (1, box_height-1):
            print(replies.move_yx(box_y_pos + i, box_x_pos) + replies.green(replies.bold("│")) + replies.on_gray21(" " * (box_width - 2)) + 
                replies.green(replies.bold('│'))) 
        #Box Title 
        print(replies.move_yx(12, box_x_pos + 34) + title)
        #Bottom Border 
        print(replies.move_yx(box_y_pos + box_height - 1, box_x_pos) + replies.green(replies.bold("└")) + replies.green(replies.bold("─")) * 
              (box_width - 2) + replies.green(replies.bold('┘'))) 
        MessageUI.input_box(mode, box_width, box_x_pos, box_y_pos, box_height)

        

    

    
        