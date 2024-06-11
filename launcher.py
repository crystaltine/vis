import time
from time import sleep
from draw_utils import *
from blessed import Terminal
import os
import sys




def print_text(text):
    
    for char in text:
        sleep(0.030)
        print(char, end='', flush=True)

def draw_loading_animation(time_limit):
    animation = "|/-\\"
    start_time = time.time()
    while True:
        for i in range(4):
            time.sleep(0.1)  # Feel free to experiment with the speed here
            sys.stdout.write("\r " + animation[i % len(animation)])
            sys.stdout.flush()
        if time.time() - start_time > time_limit:  # The animation will last for 10 seconds
            sys.stdout.write(' ')
            sys.stdout.flush()
            break


def init_starting_info():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    os.system('cls')

    print_text(f"{fcode('#12A1ED')}Welcome to {fcode('#ED125F')}Terminal Suite, {fcode('#12A1ED')}a collection of popular apps recreated in the terminal!{STYLE_CODES['reset']}'+'\n \n")
    
    print_text(f"{fcode('#12A1ED')}To run {fcode('#2FEF15')}Discord, {fcode('#12A1ED')}please type {fcode('#2FEF15')}\"run discord\".{STYLE_CODES['reset']} \n \n")
    print_text(f"{fcode('#12A1ED')}To run {fcode('#F98C10')}Geometry Dash, {fcode('#12A1ED')}please type {fcode('#F98C10')}\"run geometry_dash\".{STYLE_CODES['reset']} \n \n")


def run_apps_command():
    term=Terminal()
    init_starting_info()
    print_text(f"{fcode('#F15FDD')}...Awaiting command... \n \n")
    command=input(f"{fcode('#0953FC')}")
    print('\n')
    command=command.lower()

    while command!='run discord' and command!='run geometry_dash' and command !='q' and command!='exit' and command!='quit':

        print_text(f"{fcode('#FA2C03')}You entered an invalid command. Please try again... \n \n")
        command=input(f"{fcode('#0953FC')}")
        print('\n')
        command=command.lower()

    
    if command=='run discord':
       
        print_text(f"{fcode('#12A1ED')}Launching Discord... \n \n {fcode('#ED125F')}")
        draw_loading_animation(2)
        print_text(f"{fcode('#12A1ED')} \n \nDone... \n \n")
        time.sleep(1)
        
        os.chdir('./viscord/client')
        os.system('python main.py')

    elif command=='run geometry_dash':
        
        print_text(f"{fcode('#12A1ED')}Launching Geometry Dash... \n \n {fcode('#ED125F')}")
        draw_loading_animation(1.5)
        print_text(f"{fcode('#12A1ED')} \n \nDone... \n \n")
        time.sleep(.75)
                
        os.chdir('./gd')
        os.system('python main.py')
    
    elif command=='exit' or command=='q' or command=='quit':

        print_text(f"{fcode('#FA2C03')}Exiting... \n \n {STYLE_CODES['reset']}")
        time.sleep(1)
        sys.exit()



