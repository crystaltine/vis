import blessed 
#Creates Terminal Object + MessageUI object 
replies = blessed.Terminal()
print(replies.clear())

class Replies:
    #Terminal Height and Width 
    y = replies.height 
    x = replies.width 
    #Draw Box Function 
    def create_replies_box(box_height, box_width, box_x_pos, box_y_pos, title, content=None):
        #Top Border 
        print(replies .move_yx(box_y_pos, box_x_pos) + replies.green(replies.bold("┌")) + 
            replies.green(replies.bold("─")) * (box_width - 2) + replies.green(replies.bold("┐")))
        #Left and Right Border 
        for i in range(box_height - 2):
            if i < len(content):
                line = content[i].ljust(box_width - 4)  # Adjusting for border and padding
            else:
                line = " " * (box_width - 4)  # Fill with spaces if content ends
            print(replies.move_yx(box_y_pos + i + 1, box_x_pos) + replies.green(replies.bold("│")) +
                replies.on_gray21(line) +
                replies.green(replies.bold('│')))
        #Box Title 
        print(replies.move_yx(box_y_pos, box_x_pos + (box_width - len(title)) // 2) + title)
        #Bottom Border 
        print(replies.move_yx(box_y_pos + box_height - 1, box_x_pos) + replies.green(replies.bold("└")) + replies.green(replies.bold("─")) * 
              (box_width - 2) + replies.green(replies.bold('┘'))) 

        

    

    
        