# Vis
A collection of app remakes in the terminal. This is a recreational project and these apps are only intended for casual use.

Design Doc (Incomplete as of 1:43 AM, Jun 9): https://docs.google.com/document/d/13SuaRq5GfgQj59z0zWa9jua5XY7AGnjDIIRWVS-Cgh4/edit?usp=sharing

## Instructions for Running
```
pip install -r requirements.txt
python main.py
```

## Viscord
Viscord is a small demake of the popular chatting app Discord. It uses our own backend and user accounts, and allows for text chatting, voice chatting, and video streaming.

### More README info coming soon. For now, check out [our design doc](https://docs.google.com/document/d/13SuaRq5GfgQj59z0zWa9jua5XY7AGnjDIIRWVS-Cgh4/edit?usp=sharing)

## Untitled Geometry Dash Remake
Using ANSI color codes and block elements [listed here](https://en.wikipedia.org/wiki/Block_Elements) to make the screen look like an actual game.
Surprisingly, with correct optimizations, we have achieved framerates of around 30 per second (in most cases - but further optimizing the renderer is high priority)

### Demo video
https://github.com/crystaltine/vis/assets/114899328/9152d696-dd3b-4cfa-87c2-2a35898a1ae2

### More README info coming soon. For now, check out [our design doc](https://docs.google.com/document/d/13SuaRq5GfgQj59z0zWa9jua5XY7AGnjDIIRWVS-Cgh4/edit?usp=sharing)

### Visage
A scrapped framework inspired by HTML for creating graphical user interfaces (GUIs) inside modern terminals.

In the original iteration of the project plan, we were to create a framework that could support various elements common to webpages and desktop apps, like input boxes, buttons, divs (containers), etc. It would have handled all the things on web browsers that we often take for granted, such as automatically scrolling, determining which elements to render, which elements to render partially, and which elements to hide completely. 

However, as features were added, it became increasingly complex and harder to learn for other contributors to the project because only one of our group members was actively developing it. Development of a fully-featured framework that can handle all edge cases also proved to be extremely tedious and time consuming, and eventually it was determined that it would be better not to develop a full framework for the narrow use cases that our project would require.

However, a lot of time was still invested into Visage's development. Here are some functional features:
- Basic HTML-like elements (div, input, button, text)
- Dynamic updates and efficient rerendering
- Keyboard event listener system with keydown and keyup events
- Flexible CSS-like style definitions
- Dynamic positioning, allowing for style syntax such as `calc(50% - 5px)`
- Capability to define pseudo-ReactJS-like components using functions and directly instantiating element classes
- Automatically managed component tree which can be navigated with tab/arrow keys. However, navigation is still randomly ordered as the algorithm for determining the next closest element was never implemented.

#### Examples of usage
![An exmaple of a login screen](https://github.com/crystaltine/vis/assets/114899328/2d4b446f-9a49-41e5-a6b3-b237c8108c3d)
An example of a login screen made purely with Visage

![An example of a settings page](https://github.com/crystaltine/vis/assets/114899328/25f279e9-9e16-4e98-8f4b-13e3b991505d)
An example of a fully functional user settings customization page
