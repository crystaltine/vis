TSS_MASTER_LIST = {
    "left": int,
    "top": int,
    "right": int,
    "bottom": int,

    "position": ..., # None, relative, absolute, fixed
    "display": ..., # block, inline, grid, flex
    
    "width": int,
    "height": int,
    "padding": ..., # format: <padding>, or <padY><padX> OR <padU><padL><padD><padR>
    "margin": ..., # format: same as padding

    "backgroundColor": ..., # hex, 4-bit hex, or rgb(...)
    "border": ..., # format: <width> <color>
}
""" Maps TSS Style properties to their parsers.
For example, use the `int()` function to parse the `width` prop. """

class TSSProperties:
    """
    Implementation of style resembling a (watered-down) version of CSS.
    """

    def __init__(self, style_string: str = None, pre: dict = None):
        """
        Parses a style string into certain properties.
        """

        self.styles = {}

        if style_string is None: return

        # first get rid of any newlines:
        style_string = style_string.replace("\n", "")

        # style_string will be formatted like CSS - with semicolons to delimit
        split_styles = style_string.split(";")

        for style_item in split_styles:
            # split into key, value using the colon :

            key, value = style_item.split(":", 1)
            key = key.strip()
            value = value.strip()

            _parsefunc = TSS_MASTER_LIST.get(key)
            # ignore unknown thingies
            if _parsefunc is None: continue
            
            # TODO - throw custom error if parse fails
            self.styles[key] = _parsefunc(value)

    def __setitem__(self, key: str, value: str):
        """
        Set a style attribute with a raw TSS string.
        Does nothing if the key is not a supported TSS attribute.

        For example: `<element>.style["margin"] = "1ch 2ch"`
        """

        _parsefunc = TSS_MASTER_LIST.get(key)
        # ignore unknown thingies
        if _parsefunc is None: return
        
        # TODO - throw custom error if parse fails
        self.styles[key] = _parsefunc(value)

    def __getitem__(self, key: str):
        """
        Returns the style attribute for the style name (e.g. margin-top).
        
        Returns `None` if no attribute was set for this key.
        """
        return self.styles.get(key)