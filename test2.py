from blessed import Terminal

def check_keystroke(keystroke):
    """
    Check if the given keystroke is alphanumeric or a symbol.

    Parameters:
    - keystroke (blessed.Keystroke): The keystroke to check.

    Returns:
    - str: Description of the keystroke ('Alphanumeric' or 'Symbol' or 'Other').
    """
    # Check if the keystroke is alphanumeric (letters and numbers)
    if keystroke.isalnum():
        return "Alphanumeric"

    # Since isalnum covers letters and digits, any other typical character
    # that is printable but not whitespace can be considered a symbol.
    # We check if it's printable and not a space, tab, etc.
    elif keystroke.isprintable() and not keystroke.isspace():
        return "Symbol"
    
    # For everything else, categorize as "Other"
    return "Other"

# Usage
term = Terminal()
ks = term.inkey()  # This would block and wait for user input
result = check_keystroke(ks)
print(f"The keystroke '{ks}' is: {result}")
