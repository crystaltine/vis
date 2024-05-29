# Vis
# Vis
A collection of app remakes in the terminal. This is a recreational project and it's probably best if you don't actually use these apps.

Some Vis apps are based off a custom-built HTML-like rendering framework called [Visage (see repo here)](https://github.com/crystaltine/visage)

### Visage
A framework inspired by HTML for creating graphical user interfaces (GUIs) inside modern terminals.

**This project is currently work-in-progress** (dont use)

#### Anticipated features (hopefully (maybe))
- Basic HTML elements (div, input, button)
- Dynamic updates and efficient rerendering
- Event handler system (keyup, keydown, resize?, etc.)
- Flexible CSS-like style definitions
- React-like components
- Automatically managed component tree which can be navigated with tab/arrow keys

Usage/examples will maybe probably be added here as features get polished.# Vis
A collection of app remakes in the terminal. This is a recreational project and it's probably best if you don't actually use these apps.

Some Vis apps are based off a custom-built HTML-like rendering framework called [Visage (see repo here)](https://github.com/crystaltine/visage)

### Discord Remake - "Viscord"?**
The name is... in progress.

This remake uses the Visage framework mentioned earlier to create a dynamic graphical user interface inside the terminal. Content is sorted into actual colored panels, with buttons, input boxes, and a lot of other HTML-reminiscent features. The app will also be fully navigable using the keyboard alone.

This will feature a full account system as well as server/channel/profile functionality, friends, roles, permissions, etc. Since we can't have profile pictures, we've replaced them with symbols/emojis and custom colors users can select for their username.

### Geometry Dash Remake
Using ANSI color codes and block elements [listed here](https://en.wikipedia.org/wiki/Block_Elements) to make the screen look like an actual game.
Surprisingly, with correct optimizations, the screen doesn't actually flicker and the game is kinda (sort of) (maybe) semi-playable!!!!!!

Original docs: (Subject to change as development continues)
Flow:
1.	Home screen: play button, a level editor button, and a character customization button
2.	Levels: Play button opens up a menu with some sample levels we have created- enter to select into a level + start playing
3.	Level editor menu: hitting level editor button opens up a menu with two buttons- create new level + edit existing level

- Level editor itself: Hitting create new level button will open up a page with the level editor format as previously discussed
- Notable features: Save button to manually save the level editor, Test button to play the currently level you are making/test it out, Clear all button to wipe the entire level + start from scratch, Automative saves every [10 mins? Insert time interval here]
- Load button: Pulls up a separate page containing all the previous saves of the level, Players can navigate the saves with arrow keys + hit enter to revert back to that save, Upon hitting enter, a popup will appear asking if the player is sure that they want to revert back this version, Hitting yes one more time takes player back to the level editor with the previous save as the current state of the level, Hitting edit existing level opens up a different page containing all their saved levels, Enter to select into a level. Then same format as previous section
4.	Player icon customization: No clue how this will work yet- TBD

**Original List of App Ideas**
* Discord remake
  - Support for text chat
  - Voice chat (will not be supported in initial release of project) (also we're probably gonna be too lazy to ever add this)
  - Accounts/authentication stuff (typical)
  - Yes yes messages will be stored permanently server-side.
* Geometry Dash remake
  - Use of colored characters to create a more immersive experience rather than just ASCII art
  - Will have a built-in level editor
  - A few prebuilt levels
  - Online levels and publish feature
* Youtube remake (not currently planned)
  - Pulling videos from the actual site
  - Decoding compressed video
  - Converting to lower quality so it fits in the terminal, and also allows for decent performance (20fps?)
  - Keyboard controls for page navigation
* Chess
* Paint
* Calendar
* Todolist
* Doom
* Email
* Code Editor
* Spotify 