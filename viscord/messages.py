import blessed 
import os, sys 

message_term = blessed.Terminal()

#prints out the height and width of the terminal
#if the terminal is resized by hand, the vars will change value <- TO BE DELETED 

height = message_term.height 
width = message_term.width 

#sets the background color of the terminal using 
counter = 0 
b = True
while b:
    counter += 1
    print(message_term.on_gray21)
    if counter == 30:
        b = False 

counter2 = 0 
b2 = True
while b2:
    counter2 += 1
    print(message_term.on_gray21)
    if counter2 == 50:
        b2 = False 

print(message_term.purple(str(width)))