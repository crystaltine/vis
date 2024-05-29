from globalvars import Globals
from logger import Logger
from interpreter import read_styles, read_vis
from utils import cls, show_cursor
from div import Div
from text import Text
from scrollbox import Scrollbox
from input import Input
from button import Button
from document import Document
from key_event import KeyEvent2

from cursor import hide as hide_cursor
import requests
import json
import traceback

class mem:
    """ stores data """
    
    changes_made = False
    
    userdata: dict = {
        "username": "testuser1",
        "name_color": "#df2939",
        "symbol": "*"
    }
    
def update_display_if_first_change(doc: Document):
    if not mem.changes_made:
        mem.changes_made = True
        (d:=doc.get_element_by_id("save_status")).text = "Unsaved changes!"
        (d2:=doc.get_element_by_id("top_panel")).style['bg_color'] = "#579aff"
        d.render(), d2.render()
        
def setting_input(title: str, default_value: str, details: str = "") -> Div:
    """
    Generic component that represents one setting, which uses an input field.
    """
    return Div(
        class_str="setting_obj",
        id=f"setting_obj_{title}",
        children=[
            Text(
                class_str="setting_obj_title",
                text=title
            ),
            Text(
                class_str="setting_obj_details",
                text=details
            ),
            Input(
                class_str="setting_obj_input",
                id=f"setting_input_{title}",
                default_text=default_value,
                placeholder=f"Enter {title.lower()}...",
                on_hover=lambda: (doc.get_element_by_id(f"setting_obj_{title}").style.update({"bg_color": "#303b49"}), doc.get_element_by_id(f"setting_obj_{title}").render()),
                on_dehover=lambda: (doc.get_element_by_id(f"setting_obj_{title}").style.update({"bg_color": "#111820"}), doc.get_element_by_id(f"setting_obj_{title}").render()),
                on_change=lambda: update_display_if_first_change(doc),
            )
        ]
    )

def main(doc: Document):
    
    main_panel: Scrollbox = doc.get_element_by_id("main_panel")
    status_text: Text = doc.get_element_by_id("save_status")
    top_panel: Div = doc.get_element_by_id("top_panel")
    
    # set up page
    main_panel.add_child(setting_input("Username", mem.userdata["username"], "Maximum 32 characters"))
    main_panel.add_child(setting_input("Name Color", mem.userdata["name_color"], "Hex code of format: #RRGGBB"))
    main_panel.add_child(setting_input("Symbol", mem.userdata["symbol"], "Maximum 1 character"))
    
    def upload_user_settings_changes(changes: dict) -> None:
        """
        Uploads changes made to user settings on this page to the server, and manages the
        page based on the result (renders a success message, invalid, failure, etc.)
        
        
        `changes` format:
        {
            "setting_name": "new_value"
        }
        Should only contain keys of settings that have been changed.
        """
        res = requests.post("http://127.0.0.1:5000/api/login", json=changes)
        data = res.json()
        
        if data['type'] == 'success':
            mem.userdata = data['new_userdata']
            status_text.text = "Changes saved!"
            top_panel.style['bg_color'] = "#5eca6b"
        elif data['type'] == 'invalid':
            status_text.text = f"Did not save because {", ".join(data['invalid_fields'])} are invalid."
            top_panel.style['bg_color'] = "#c66d5e"
        else: 
            Logger.log(f"login attempt failed! (server err or smth)")
            status_text.text = "Failed to save changes! Try again later"
            top_panel.style['bg_color'] = "#ac5a4b"
            
        status_text.render()
        
    def TEMP_upload_user_settings_changes() -> None:
        # just for ui testing. pretend server successfully saved data
        #mem.userdata.update(changes)
        status_text.text = "Changes saved!"
        top_panel.style['bg_color'] = "#5eca6b"
        top_panel.render()
        mem.changes_made = False
    
    def on_key(keyevent: KeyEvent2):
        if keyevent.key == '\x13': # ctrl+s -> save
            TEMP_upload_user_settings_changes()
            
    doc.add_event_listener(on_key)
    doc.mount()
    
if __name__ == "__main__":
    
    read_styles("user_settings.tss")
    read_vis("user_settings.vis")
    
    with (doc:=Globals.__vis_document__).term.cbreak():
        try:
            hide_cursor()
            main(doc)
            show_cursor()
        except Exception as e:
            cls()
            Logger.log(f"EXCEPTION [user_settings/main]: {traceback.format_exc()}")
            Logger.write()
            print(f"\x1b[31mdiscoword :3 fatal: an error occurred, \x1b[33m{traceback.format_exc()}\x1b[0m")
            exit()