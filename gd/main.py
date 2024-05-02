import blessed
import GDMenu
from GDMenu import draw_button0, draw_button1, draw_button2, draw_text, draw_square
import os 

terminal = blessed.Terminal()

def main():

    # Reset scren to black

    draw_square(terminal.width, terminal.height, 0, 0, 'black')

    # Drawing 3 buttons onto screen with middle button selected by default

    draw_button0()
    draw_button1(True)
    draw_button2()

    current_index=1
    
    with terminal.hidden_cursor():

        while True:
            
            title='VEOMETRY DASH'
            draw_text(title, int(terminal.width*0.45), int(terminal.height*0.1))
            
            with terminal.cbreak():
                changed=False
                old_index=0

                val = terminal.inkey(timeout=1)

                # Quitting game if q is hit

                if val == "q":
                    break

                # Arrow keys to select a different button

                if val.name=='KEY_LEFT':
                    old_index=current_index
                    changed=True
                    
                    current_index-=1
                    if current_index<0:
                        current_index=2
                    
                if val.name=='KEY_RIGHT':
                    old_index=current_index
                    changed=True
                    current_index+=1
                    if current_index>2:
                        current_index=0

                # Running test gd file if space is selected

                if val==' ' and current_index==1:
                    os.system('python run_gd.py')


                # If a button has been pressed, we rerender the new button and the previous button to get rid of/add in the white outline

                if changed:
                    
                    # Rerendering the new buttons

                    deselect_prev_button = getattr(GDMenu, 'draw_button'+str(old_index))
                    deselect_prev_button()

                    select_new_button = getattr(GDMenu, 'draw_button'+str(current_index))
                    select_new_button(True)

main()
