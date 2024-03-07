def round_nearest_quarter(x: float) -> float:
    """
    Returns the nearest quarter to x. 
    Supports negative numbers too!
    
    Examples:
    - `0.1` -> `0`
    - `2.99` -> `3.0`
    - `-1.13` -> `-1.25`
    """
    rounded = round(x * 4) / 4
    return rounded

inp = input("Enter a number to test or q to quit: ")
while inp.lower() != 'q':
    try:
        x = float(inp)
        print(f"{x} rounded to quarter is {round_nearest_quarter(x)}")
    except ValueError:
        print("Invalid input")
    inp = input("Enter a number to test or q to quit: ")