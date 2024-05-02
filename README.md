# Vis
A framework for rendering HTML-like documents using monospace characters.

**Objectives for Framework**

* Component tree - move around components using arrow keys + press enter to click buttons or enter inputs
* Implement key listener for commands- have set of every keybind we want (ex: cntrl q), every frame, see if any of them intersect
* Each app has an command to open it- you type in the name of the app you want to openn and it opens
* You can also install apps from the framework (similar to package manager or app store where you can install apps)
* We need basic html components- panels/divs, inputs, buttons, dropdowns, hyperlinks, images (maybe, not a first priority), standard text tab. Each of them should have size and position attributes and a z dimension for layers

**Geometry Dash**

General Bindings:
- Arrow keys to hover over a different level
- Enter to select
- B to go back to previous screen

Flow:
1.	Home screen: play button, a level editor button, and a character customization button
2.	Levels: Play button opens up a menu with some sample levels we have created- enter to select into a level + start playing
3.	Level editor menu: hitting level editor button opens up a menu with two buttons- create new level + edit existing level

- Level editor itself: Hitting create new level button will open up a page with the level editor format as previously discussed
- Notable features: Save button to manually save the level editor, Test button to play the currently level you are making/test it out, Clear all button to wipe the entire level + start from scratch, Automative saves every [10 mins? Insert time interval here]
- Load button: Pulls up a separate page containing all the previous saves of the level, Players can navigate the saves with arrow keys + hit enter to revert back to that save, Upon hitting enter, a popup will appear asking if the player is sure that they want to revert back this version, Hitting yes one more time takes player back to the level editor with the previous save as the current state of the level, Hitting edit existing level opens up a different page containing all their saved levels, Enter to select into a level. Then same format as previous section
4.	Player icon customization: No clue how this will work yet- TBD



**Schedule**
- 1 week for testing if windows in terminal can work (and making it work) AND a master-app ***(3/7)***
- 2 weeks for discord de-make ***(3/21)***
- 4 weeks for geometry dash de-make ***(4/18)***
- 5 weeks for youtube? ***(5/23)***
- any extra time? polishing apps, branching off into solo apps
  
**List of App Ideas:**
* Discord
  - text chat
  - voice chat (***HARD MAYBE***)
  - basic authentication
  - server-side message storing
* geometry dash
  - level renderer
  - physics
  - level editor
  - menus
  - maybe server for levels
* youtube
  - getting videos
  - decoding
  - playing
  - controls
  - audio


* Chess
* Paint
* Calendar
* Todolist
* Doom
* Geometry Dash
* Email
* Code Editor
* Spotify 
