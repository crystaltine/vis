import blessed 

# Creates Terminal Object 
message_term = blessed.Terminal()

print(message_term.clear)
mode = 0

class MessageUI:
    # Terminal Height and Width 
    y = message_term.height 
    x = message_term.width  
    
    @staticmethod
    def input_box(mode:int, box_width:int, box_x_pos:int, box_y_pos:int, box_height:int, input_text:str=""):
        # Check mode for input box
        if mode == 0:
            input_text = ""
            input_box_width = box_width - 4
            input_box_x_pos = box_x_pos + 2
            input_box_y_pos = box_y_pos + box_height - 2
            
            # Draw input box
            print(message_term.move_yx(input_box_y_pos, input_box_x_pos) + message_term.blue(message_term.bold("└")) + 
                  message_term.blue(message_term.bold("─")) * (input_box_width - 1) + message_term.blue(message_term.bold("┘")))
            
            # Start capturing input
            with message_term.cbreak():
                while True:
                    # Move cursor to input box
                    print(message_term.move_yx(input_box_y_pos, input_box_x_pos + 1), end='')
                    # Get user input
                    input_text = ""
                    key = message_term.inkey()
                    if key.is_sequence:
                        if key.name == "KEY_ENTER":
                            break
                        elif key.name == "KEY_BACKSPACE":
                            input_text = input_text[:-1]
                        # Other key handling if needed
                    else:
                        input_text += key

                    # Clear input box and redraw input
                    print(" " * (input_box_width - 1), end='')
                    print(message_term.bold(input_text), end='')

    # Draw Box Function 
    @staticmethod
    def box_creator(box_height:int, box_width:int, box_x_pos:int, box_y_pos:int, title:str, mode:int):
        # Top Border 
        print(message_term.move_yx(box_y_pos, box_x_pos) + message_term.blue(message_term.bold("┌")) + 
            message_term.blue(message_term.bold("─")) * (box_width - 2) + message_term.blue(message_term.bold("┐")))
        # Left and Right Border 
        for i in range (1, box_height-1):
            print(message_term.move_yx(box_y_pos + i, box_x_pos) + message_term.blue(message_term.bold("│")) + message_term.on_gray21(" " * (box_width - 2)) + 
                message_term.blue(message_term.bold('│'))) 
        # Box Title 
        print(message_term.move_yx(box_y_pos - 18, box_x_pos + 32) + title)
        # Bottom Border 
        print(message_term.move_yx(box_y_pos + box_height - 1, box_x_pos) + message_term.blue(message_term.bold("└")) + message_term.blue(message_term.bold("─")) * 
              (box_width - 2) + message_term.blue(message_term.bold('┘')))
        
        MessageUI.input_box(mode, box_width, box_x_pos, box_y_pos, box_height)
