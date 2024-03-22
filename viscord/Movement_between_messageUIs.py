from messages import MessageUI
from pinned_messages import PinnedMessageUI
import blessed

class Message_UI_Movement: 
    term = blessed.Terminal()
    print(term.clear())
    MessageUI.box_creator(25, 75, 30, 20, term.green_on_gray21(term.bold("Viscord Chat"))) 
    while True: 
        with term.cbreak(): 
            pinned_open_key_bind = 'p'
            main_open_key_bind = 'm'
            if term.inkey() == pinned_open_key_bind:
                print(term.clear())
                PinnedMessageUI.create_a_box(25, 75, 30, 20, term.purple_on_gray21(term.bold("Pinned Messages"))) 
            if term.inkey() == main_open_key_bind:
                print(term.clear())
                MessageUI.box_creator(25, 75, 30, 20, term.green_on_gray21(term.bold("Viscord Chat")))   