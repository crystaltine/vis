import blessed 

# Creates Terminal Object 
message_term = blessed.Terminal()

print(message_term.clear)
mode = 0

class MessageUI:
    # Terminal Height and Width 
    y = message_term.height 
    x = message_term.width  
    
    # Draw Box Function 
    @staticmethod
    def box_creator(box_height, box_width, box_x_pos, box_y_pos, title, mode=0):
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

class Message_UI_Movement: 
    print(message_term.clear())
    MessageUI.box_creator(25, 75, 30, 20, message_term.green_on_gray21(message_term.bold("Viscord Chat")), mode)
    
    @staticmethod
    def main(term):
        while True: 
            with term.cbreak(): 
                pinned_open_key_bind = 'p'
                main_open_key_bind = 'm'
                replies_open_key_bind = 'r'
                if term.inkey() == pinned_open_key_bind:
                    print(term.clear())
                    MessageUI.box_creator(25, 75, 30, 20, term.purple_on_gray21(term.bold("Pinned Messages")), mode=1)
                    mode = 1
                if term.inkey() == main_open_key_bind:
                    print(term.clear())
                    MessageUI.box_creator(25, 75, 30, 20, term.green_on_gray21(term.bold("Viscord Chat")), mode=0) 
                    mode = 0  
                if term.inkey() == replies_open_key_bind:
                    print(term.clear()) 
                    MessageUI.box_creator(25, 75, 30, 20, term.red_on_gray21(term.bold("Replies")), mode=3)

class RunUI:
    Message_UI_Movement.main(term)
