from cursor import hide
from globalvars import Globals
from logger import Logger
from interpreter import read_styles, read_vis
from utils import cls, show_cursor
from div import Div
from text import Text
from scrollbox import Scrollbox
from input import Input
from button import Button

def main():
    
    def setting_input(title: str, desc: str, default_value: str):
        """
        Generic component that represents one setting, which uses an input field.
        """
        return Div(
            class_str="setting_obj",
            children=[
                Text(
                    class_str="setting_obj_title",
                    text=title
                ),
                Text(
                    class_str="setting_obj_desc",
                    text=desc
                ),
                Input(
                    class_str="setting_obj_input",
                    placeholder=default_value # TODO - make a def. value field instead of using placeholder
                )
            ]
        )
    
if __name__ == "__main__":

    hide()
    
    read_styles("user_settings.tss")
    read_vis("user_settings.vis")
    
    with Globals.__vis_document__.term.cbreak():
        try:
            main()
            show_cursor()
        except Exception as e:
            Logger.log(f"EXCEPTION [user_settings/main]: {e}")
            Logger.write()
            cls()
            print(f"\x1b[31mdiscoword :3 fatal: an error occurred, \x1b[33m{e}\x1b[0m")
            exit()