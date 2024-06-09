from typing import Literal
from time import sleep, time_ns, time
from gd_constants import GDConstants

from logger import Logger
from menus.main_menu import MainMenu
from menus.official_levels_menu import OfficialLevelsMenu
from menus.custom_levels_menu import CustomLevelsMenu
from menus.create_level_menu import CreateLevelMenu
from menus.created_levels_menu import CreatedLevelsMenu
from menus.online_levels_menu import OnlineLevelsMenu
from editor.level_editor import LevelEditor

from game import Game
from level import Level

class MenuHandler:
    """ General class that manages the game's menu flow 
    (i.e. which menu is currently being displayed, moving between menus, etc.) """
    
    MENU_LIST = {
        'main': MainMenu,
        'custom_levels': CustomLevelsMenu,
        'official_levels': OfficialLevelsMenu,
        'create_new': CreateLevelMenu,
        'created_levels': CreatedLevelsMenu,
        'online_levels': OnlineLevelsMenu,
        
    }
    
    PREV_PAGES = {
        "custom_levels": "main",
        "official_levels": "main",
        "create_new": "custom_levels",
        "created_levels": "custom_levels",
        "online_levels": "custom_levels",
    }
    """ Guide for which page to go back to when the escape key is pressed """
    
    current_page: str = 'main'
    """ should be a value from MenuHandler.MENU_LIST, represents the current menu being displayed """
    
    running = False
    
    not_in_menu = False
    
    def run():
        """ 
        Initializes the game menu system, rendering the main menu and beginning the key input loop 
        
        Since this function leads into the gameloop and level editor loop, it is BLOCKING.
        """
        
        MenuHandler.running = True
        MenuHandler._render_page(MenuHandler.current_page)
        
        while True:
            
            if not MenuHandler.running:
                break
            if MenuHandler.not_in_menu:
                sleep(0.01) # do nothing if in level or editor, they have their own loops
                continue
            
            val = ...
            with GDConstants.term.cbreak():
                val = GDConstants.term.inkey()
                
            # return to prev editor/quit game if q or escape is hit
            if (val or val.name) in GDConstants.QUIT_KEYS:
                if MenuHandler.current_page == 'main':
                    MenuHandler.running = False
                    break
                else:
                    prev_page = MenuHandler.PREV_PAGES[MenuHandler.current_page]
                    MenuHandler._render_page(prev_page)
            
            # otherwise, pass the key input to the current menu
            else:
                #Logger.log(f"[MenuHandler] sending key {val.name} to {MenuHandler.current_page}")
                action = MenuHandler.MENU_LIST[MenuHandler.current_page].on_key(val)
                #Logger.log(f"[MenuHandler] action: {action}")
                match action:
                    
                    ### MAIN MENU PAGE
                    case "quit":
                        #Logger.log("[MenuHandler] quitting game")
                        MenuHandler.running = False
                        return
                    case "play":
                        MenuHandler._render_page("official_levels")
                    case "editor":
                        MenuHandler._render_page("custom_levels")  
                    case "play_level":
                        
                        MenuHandler.run_level(OfficialLevelsMenu.get_selected_level_filepath())
                    
                    ### CUSTOM LEVELS PAGE
                    case "create_new_level":
                        MenuHandler._render_page("create_new")
                    case "open_created_levels":
                        MenuHandler._render_page("created_levels")
                    case "open_online_levels":
                        MenuHandler._render_page("online_levels")

                    ### CREATED LEVELS PAGE
                    case "play_created_level":
                        MenuHandler.run_level(CreatedLevelsMenu.get_selected_level_filepath())
                    case "edit_current_level":
                        MenuHandler.edit_level(CreatedLevelsMenu.get_selected_level_filepath())
                        
                    ### CREATE NEW LEVEL PAGE
                    case "goto_custom_levels_menu":
                        MenuHandler._render_page("custom_levels")
                    case "goto_created_levels_menu":
                        MenuHandler._render_page("created_levels")
    
    def run_level(filepath: str) -> None:
        
        """ Enters into the actual level loop, running the specified level file """

        MenuHandler.not_in_menu = True

        game = Game(Level.parse_from_file(filepath))
        game.start_level()
        
        MenuHandler.not_in_menu = False
        if "official" in game.level.filepath:
            MenuHandler._render_page("official_levels")
        else:
            MenuHandler._render_page("created_levels")
        
        # clear terminal inkey buffer
        with GDConstants.term.cbreak():
            while GDConstants.term.inkey(timeout=0.01):
                pass
    
    def edit_level(filepath: str) -> None:
        
        """ Enters into the actual level loop, running the specified level file """

        MenuHandler.not_in_menu = True

        editor=LevelEditor(filepath)
        editor.run_editor()

        # when run_editor() returns, go back to created levels menu
        MenuHandler.not_in_menu = False
        MenuHandler._render_page("created_levels")
        
        # clear terminal inkey buffer
        with GDConstants.term.cbreak():
            while GDConstants.term.inkey(timeout=0.01):
                pass
            
    def _render_page(page_name: str, *args, **kwargs) -> None:
        """ Renders the specified menu page and updates the current page field, 
        optionally allowing extra params for the render() method """
        MenuHandler.current_page = page_name
        MenuHandler.MENU_LIST[MenuHandler.current_page].render(*args, **kwargs)
        