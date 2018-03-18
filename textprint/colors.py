from enum import Enum
from typing import Union

"""
This file serves as place to store the class Color which is an abstraction for the colorama classes: Fore, Back, & Style
"""

# thanks https://github.com/tartley/colorama/blob/master/colorama/ansi.py
CSI = "\033["  # str(CSI)
CLEAR_LINE = CSI + str(2) + "K"


def code(*args):
    parts = []
    for arg in args:
        if isinstance(arg, list):
            parts.extend(arg)
        else:
            parts.append(arg)
    middle = ""
    for element in parts:
        if len(middle) != 0:
            middle += ";"
        middle += str(element)

    return CSI + middle + "m"


class Color(Enum):
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    GREY = [37, 2]
    COLOR_RESET = 39

    BOLD = 1
    NORMAL = 22
    """AKA STYLE_RESET"""
    DIM = 2

    BACK_BLACK = 40
    BACK_RED = 41
    BACK_GREEN = 42
    BACK_YELLOW = 43
    BACK_BLUE = 44
    BACK_MAGENTA = 45
    BACK_CYAN = 46
    BACK_GREY = 47
    """If you want to reset the background, it is recommended to use BACK_RESET"""
    BACK_RESET = 49

    RESET = 0  # str(Style.RESET_ALL)
    """Used to reset everything back to normal. Should be used instead of TOTAL_RESET whenever possible because \
            this may be interpreted differently by OutputSender implementations"""
    # TOTAL_RESET = str(Fore.RESET) + str(Style.NORMAL) + str(Back.RESET)
    # """Used to reset the text completely back to normal. Not the same as RESET."""

    CLEAR_SECTION = CSI + "2J"

    def __str__(self):  # an enum's default str would be RED for something like RED (The name of the variable)
        if isinstance(self.value, str):
            return self.value
        return code(self.value)

    def __add__(self, other):
        if isinstance(other, Color):
            return code(self.value, other.value)
        return str(self) + str(other)

    def __radd__(self, other):
        if isinstance(other, Color):
            return code(other.value, self.value)
        return str(other) + str(self)

    def __rshift__(self, other):  # color >> text
        reset = self.__class__.RESET
        if isinstance(other, str):
            if other.endswith(str(self.__class__.RESET)):
                reset = ""
        return self + other + reset

    def __rlshift__(self, other):  # text << color
        return self.__rshift__(other)

    @classmethod
    def get_color(cls, string_color: str) -> Union['Color', bool]:
        """
        Note should should check whether or not the passed string_color starts with CSI or an assert error will rise

        Note does not count CSI since that would make this method mostly pointless

        :param string_color: The string code of the color. Note if this contains any text other than the color, \
                this method will return None
        :return: The color object or a bool that's True if any of the colors start with the passed string_color
        """
        r = False
        for color in cls:
            # if color == cls.CSI:
            #     continue
            if str(color) == string_color:
                return color
            if not r:
                r = str(color).startswith(string_color)

        return r
