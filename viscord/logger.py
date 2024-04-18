class Logger:
    """
    Simple logger that autocolors messages
    """

    def info(message: str, prefix: str = ""):
        """
        Prints `"info: message"` in blue. If `prefix` is provided, adds it to the
        front of the message in white.
        """
        print(f"\x1b[0m{prefix}\x1b[34m info: {message}\x1b[0m")

    def warn(message: str, prefix: str = ""):
        """
        Prints `"warning: message"` in yellow. If `prefix` is provided, adds it to the
        front of the message in white.
        """
        print(f"\x1b[0m{prefix}\x1b[33m warning: {message}\x1b[0m")

    def success(message: str, prefix: str = ""):
        """
        Prints `"success: message"` in green. If `prefix` is provided, adds it to the
        front of the message in white.
        """
        print(f"\x1b[0m{prefix}\x1b[32m success: {message}\x1b[0m")

    def err(message: str, prefix: str = ""):
        """
        Prints `"ERROR: message"` in red. If `prefix` is provided, adds it to the
        front of the message in white.
        """
        print(f"\x1b[0m{prefix}\x1b[31m ERROR: {message}\x1b[0m")