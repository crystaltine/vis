import cursor
import sys
import registry
import config
import uuid
import server_select
import requests
import blessed
import colors
import keyshortcuts
sys.path.append("../..")
import launcher

term = blessed.Terminal()

FIELD_WIDTH = int(term.width * 0.4 - 8) - 1

global selection
selection = 0

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def draw_background():
    print(term.home + term.clear, end=" ")
    for y in range(term.height):
        print(term.move(y, 0) + term.on_color_rgb(*hex_to_rgb(colors.background)) + ' ' * term.width, end="")


def draw_menu():
    tlx = int(term.width * 0.3)
    tly = int(term.height * 0.2)

    for y in range(tly, tly + int(term.height * 0.6)):
        print(term.move(y, tlx) + term.on_color_rgb(*hex_to_rgb(colors.div)) + ' ' * int(term.width * 0.4), end="")

    print(term.move(tly-1, tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.background)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + "▄" * int(term.width * 0.4 + 2), end="")
    print(term.move(tly + int(term.height * 0.6), tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.background)) + term.color_rgb(*hex_to_rgb(colors.div_shadow)) + "▀" * int(term.width * 0.4 + 2), end="")
    for y in range(tly, tly + int(term.height * 0.6)):
        print(term.move(y, tlx-1) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + " ", end="")
        print(term.move(y, tlx + int(term.width * 0.4)) + term.on_color_rgb(*hex_to_rgb(colors.div_shadow)) + " ", end="")



def center_text(text):
    return int(term.width / 2 - len(text) / 2)

def draw_all_text():
    x = center_text("Welcome to Viscord.")
    print(term.move(int(term.height*0.35) - 2, x) + term.on_color_rgb(*hex_to_rgb(colors.div)) + term.color_rgb(*hex_to_rgb(colors.header)) + "Welcome to Viscord.", end="")

    x = center_text("Select an option below")
    print(term.move(int(term.height*0.35) - 1, x) + term.color_rgb(*hex_to_rgb(colors.header)) + "Select an option below", end="")

    x = center_text("Esc to exit")
    print(term.move(int(term.height*0.2), x) + term.color_rgb(*hex_to_rgb(colors.note_text)) + "Esc to exit", end="")
    

def draw_buttons():
    global selection
    c1 = c2 = colors.button
    if selection == 0:
        c1 = colors.button_selected
    elif selection == 1:
        c2 = colors.button_selected
    
    
    x = center_text("   Log In   ")
    print(term.move(int(term.height*0.5), x) + term.color_rgb(*hex_to_rgb(colors.text)) + term.on_color_rgb(*hex_to_rgb(c1)) + " " * 3 + "Log In" + " " * 3, end="")

    
    x = center_text("  Register  ")
    print(term.move(int(term.height*0.5) + 2, x) + term.color_rgb(*hex_to_rgb(colors.text)) + term.on_color_rgb(*hex_to_rgb(c2)) + " " * 2 + "Register" + " " * 2, end="")



def redraw_all():
    print(term.clear)
    draw_background()
    draw_menu()
    draw_all_text()
    draw_buttons()
    print(term.normal, flush=True)


    

def main():
    cursor.hide()
    if len(sys.argv) > 1 and sys.argv[1] == "kill":
        registry.del_reg("cache")
    global selection

    try:
        requests.get(f"https://{config.HOST}:{config.PORT}")
    except Exception as e:
        print(term.red + f"Could not establish a connection to the Viscord server at {config.HOST}:{config.PORT}, exiting..." + term.normal)
        cursor.show()
        sys.exit(1)

    if registry.get_reg("cache"):
        
        cache = registry.get_reg("cache")
        sys_uuid = str(uuid.getnode())
        try:
            resp = requests.post(f"https://{config.HOST}:{config.PORT}/api/login/bypass", json={"cache": cache, "sys_uuid": sys_uuid})
            if resp.status_code == 200:
                try:
                    server_select.main(resp.json()["token"])
                except Exception as e:
                    print(term.red + "An error occurred while trying to bypass the login, please log in manually." + term.normal)
                    print(e)
                    

                sys.exit(0)
            elif resp.status_code != 500:
                print(term.red + f"Could not establish a connection to the Viscord server at {config.HOST}:{config.PORT}, exiting..." + term.normal)
                sys.exit(1)
                
        except Exception as e:
            pass

    redraw_all()

    with term.cbreak():
        val = ""
        while True:
            sx = term.width
            sy = term.height
            val = term.inkey(timeout=0.01)
            if not val:
                if term.width != sx or term.height != sy:
                    redraw_all()
                continue
            
            if val.code == term.KEY_ESCAPE:
                print(term.clear, end="")
                print(term.normal, end="")
                cursor.show()
                #launcher.run_apps_command()
                break

            if val.code == term.KEY_ENTER:
                if selection == 0:
                    import login_menu
                    login_menu.main()
                elif selection == 1:
                    import register
                    register.main()
                redraw_all()
                continue
            if repr(val) in keyshortcuts.back_keys:
                selection = max(0, selection - 1)
                draw_buttons()
                print("")
            elif repr(val) in keyshortcuts.next_keys:
                selection = min(1, selection + 1)
                draw_buttons()
                print("")
            
            

if __name__ == "__main__":
    main()