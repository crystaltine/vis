import blessed 

#Creates Terminal Object + repliesUI object 
replies = blessed.Terminal()
print(replies.clear())

class Replies:
    #Terminal Height and Width 
    y = replies.height 
    x = replies.width 


    input_text = ""
    @staticmethod
    def input_box(mode:int, box_width:int, box_x_pos:int, box_y_pos:int, box_height:int):
        # Check mode for input box
        if mode == 0:
            global input_text
            input_text = ""
            input_box_width = box_width - 4
            input_box_x_pos = box_x_pos + 2
            input_box_y_pos = box_y_pos + box_height - 2
            # Draw input box
            print(replies.move_yx(input_box_y_pos, input_box_x_pos) + replies.blue(replies.bold("└")) + 
                  replies.blue(replies.bold("─")) * (input_box_width - 1) + replies.blue(replies.bold("┘")))
            
            # Start capturing input
            with replies.cbreak():
                while True:
                    # Move cursor to input box
                    print(replies.move_yx(input_box_y_pos, input_box_x_pos + 1), end='')
                    # Get user input
                    global input_text
                    input_text = ""
                    key = replies.inkey()
                    if key.is_sequence:
                        if key.name == "KEY_ENTER":
                            break
                        elif key.name == "KEY_BACKSPACE":
                            global input_text
                            input_text = input_text[:-1]
                        # Other key handling if needed
                    else:
                        global input_text
                        input_text += key
                    # Clear input box and redraw input
                    print(" " * (input_box_width - 1), end='')
                    print(replies.bold(input_text), end='')

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
        Replies.input_box(mode, box_width, box_x_pos, box_y_pos, box_height)

        

    

    
        