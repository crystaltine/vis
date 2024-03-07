import blessed 
import os, sys 

message_term = blessed.Terminal()

#prints out the height and width of the terminal
#if the terminal is resized by hand, the vars will change value <- TO BE DELETED 

height = message_term.height 
width = message_term.width 
print(message_term.clear)

while True:
    print(message_term.on_blue) 



print("width: " + str(width) + " , " + " height: " + str(height))


