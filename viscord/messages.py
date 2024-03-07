import blessed 
import os, sys 


chat_term = blessed.Terminal()

#prints out the height and width of the terminal
#if the terminal is resized by hand, the vars will change value <- TO BE DELETED 

height = chat_term.height 
width = chat_term.width 
print("width: " + str(width) + " height: " + str(height))



