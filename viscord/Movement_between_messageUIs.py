from messages import MessageUI
from pinned_messages import PinnedMessageUI
from replies import Replies
import blessed

class Message_UI_Movement: 
    term = blessed.Terminal()
    print(term.clear())
    MessageUI.box_creator(25, 75, 30, 20, term.green_on_gray21(term.bold("Viscord Chat"))) 
    
    def movement(term):
        while True: 
            with term.cbreak(): 
                pinned_open_key_bind = 'p'
                main_open_key_bind = 'm'
                replies_open_key_bind = 'r'
                if term.inkey() == pinned_open_key_bind:
                    print(term.clear())
                    PinnedMessageUI.create_pinned_messages_box(25, 75, 30, 20, term.purple_on_gray21(term.bold("Pinned Messages"))) 
                if term.inkey() == main_open_key_bind:
                    print(term.clear())
                    MessageUI.box_creator(25, 75, 30, 20, term.green_on_gray21(term.bold("Viscord Chat")))   
                if term.inkey() == replies_open_key_bind:
                    print(term.clear()) 
                    Replies.create_replies_box(15, 75, 30, 50, term.red_on_gray21(term.bold("Replies")), "")


 
                 