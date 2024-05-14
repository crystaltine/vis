from blessed import Terminal

class GD:
    """
    General class for broad game elements.
    Currently used for holding THE terminal instance, accessible from all parts of the game.
    """
    
    term = Terminal()