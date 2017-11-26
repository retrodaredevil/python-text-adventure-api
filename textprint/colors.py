from enum import Enum
from typing import Optional, Union

from colorama import Fore, Back, Style
from colorama.ansi import CSI

"""
This file serves as place to store the class Color which is an abstraction for the colorama classes: Fore, Back, & Style
"""


class Color(Enum):
    RED = str(Fore.RED)
    GREEN = str(Fore.GREEN)
    YELLOW = str(Fore.YELLOW)
    BLUE = str(Fore.BLUE)
    MAGENTA = str(Fore.MAGENTA)
    CYAN = str(Fore.CYAN)
    WHITE = str(Fore.WHITE)
    GREY = str(Fore.WHITE) + str(Style.DIM)
    COLOR_RESET = str(Fore.RESET)

    BOLD = str(Style.BRIGHT)
    NORMAL = str(Style.NORMAL)
    """AKA STYLE_RESET"""
    DIM = str(Style.DIM)

    BACK_RED = str(Back.RED)
    BACK_GREEN = str(Back.GREEN)
    BACK_YELLOW = str(Back.YELLOW)
    BACK_BLUE = str(Back.BLUE)
    BACK_MAGENTA = str(Back.MAGENTA)
    BACK_CYAN = str(Back.CYAN)
    BACK_GREY = str(Back.WHITE)
    BACK_BLACK = str(Back.BLACK)
    """If you want to reset the background, it is recommended to use BACK_RESET"""
    BACK_RESET = str(Back.RESET)

    RESET = str(Style.RESET_ALL)
    """Used to reset everything back to normal. Should be used instead of TOTAL_RESET whenever possible because \
            this may be interpreted differently by PlayerOutput implementations"""
    TOTAL_RESET = str(Fore.RESET) + str(Style.NORMAL) + str(Back.RESET)
    """Used to reset the text completely back to normal. Not the same as RESET."""

    ESCAPE = str(CSI)
    """The escape character that is at the front of all the values in this enum."""

    # def value(self):
    #     return self.value

    def __str__(self):  # an enum's default str would be RED for something like RED (The name of the variable)
        return self.value

    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)

    def __rshift__(self, other):  # color >> text
        return self + other + self.__class__.RESET

    def __rlshift__(self, other):  # text << color
        return self.__rshift__(other)

    @classmethod
    def get_color(cls, string_color: str) -> Union['Color', bool]:
        """
        Note should should check whether or not the passed string_color starts with ESCAPE or an assert error will rise

        :param string_color: The string code of the color. Note if this contains any text other than the color, \
                this method will return None
        :return: The color object or a bool that's True if any of the colors start with the passed string_color
        """
        r = False
        for color in cls:
            if str(color) == string_color:
                return color
            if not r:
                r = str(color).startswith(string_color)

        return r
