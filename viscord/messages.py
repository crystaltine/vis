import blessed 
import os, sys 

message_term = blessed.Terminal()

#prints out the height and width of the terminal
#if the terminal is resized by hand, the vars will change value <- TO BE DELETED 

height = message_term.height 
width = message_term.width 
counter = 0 
counter2 = 0 
b = True
b2 = True

#sets the background color of the terminal 
while b:
    counter += 1
    print(message_term.on_gray21)
    if counter == width:
        b = False 

while b2:
    counter2 += 1
    print(message_term.on_gray21)
    if counter2 == height:
        b2 = False

print(str(width))
print(message_term.normal) 