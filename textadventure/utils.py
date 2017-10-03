import sys
from difflib import SequenceMatcher
from typing import Union, List, Tuple

"""
Imports should not import any of the other modules we've made. It could conflict when trying to import utils
"""

MessageConstant = Union[str, 'Message']
"""MessageConstant is used to represent a constant Message or string object that does not change"""

NOT_IMPORTANT = ["the", "into", "to", "of", "with", "and", "in", "that", "my", "at", "near", "around", "his", "her",
                 "their", "our", "your", "from"]
"""
Represents a list of strings that are unimportant to comparing input with. Note all words in list are lower case
These words may be important in determining what someone wants in an english sentence, however, since we aren't \
    interpreting an english paper, we should be OK.
"""

CanDo = Tuple[bool, MessageConstant]
"""[0] is a boolean representing if a player can do the action. If [0] is True, then [1] tells why it is True. If\
False, then [1] is an error message that should be sent to the player"""


def debug(values):
    """
    Used to debug things
    @param values: The values to print
    """
    print(values, file=sys.stderr)
    sys.stdout.flush()


def error(values):
    """
    Should be used to print errors when raising an exception won't do what you want.
    @param values: The values to print
    """
    debug(values)


def is_string_true(string_input: str):
    return "y" in string_input.lower()


def get_unimportant(to_change: List[str], unimportant_list=NOT_IMPORTANT) -> List[int]:
    """
    Should be used for comparing input to a string. If the input will eventually be outputted, don't print this, \
        you should print the input so the player knows what they actually inputted.
    @param to_change: The list of separated words
    @param unimportant_list: The list of words that are unimportant
    @return: A list of ints where each int corresponds to an index in the to_change list that is unimportant
    """

    r: List[int] = []
    for index, s in enumerate(to_change):
        test = s
        test = test.lower()
        while test.endswith(".") or test.endswith("!") or test.endswith("?"):
            test = test[:-1]  # removes last character
        if test in unimportant_list:
            r.append(index)

    return r


def are_mostly_equal(a: str, b: str) -> bool:
    def remove_for(change: str):
        split = change.split(" ")

        unimportant = get_unimportant(split)
        important = []
        for index, s in enumerate(split):
            if index not in unimportant:
                important.append(s)
        return " ".join(important)

    a = remove_for(a).lower()
    b = remove_for(b).lower()

    ratio = SequenceMatcher(a=a, b=b).ratio()
    return ratio >= .95


class Point:
    def __init__(self, x: int, y: int, z: int = 0):
        """
        Used on locations by having an x, y and z position (z is normally 0)
        @param x: The x position on the map
        @param y: The y position on the map
        @param z: Used for the height/level (usually 0)
        """
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other):
        if type(other) is int:
            return Point(self.x * other, self.y * other, self.z * other)
        return Point(self.x * other.x, self.y * other.y, self.z * other.z)

    def __add__(self, other):
        if type(other) is int:
            return Point(self.x + other, self.y + other, self.z + other)
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return self + (other * -1)

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return super(Point, self).__eq__(other)

    def __str__(self):
        return "Point(x:{},y:{},z:{})".format(self.x, self.y, self.z)


NORTH = Point(0, 1)
EAST = Point(1, 0)
SOUTH = Point(0, -1)
WEST = Point(-1, 0)
UP = Point(0, 0, 1)
DOWN = UP * -1
ZERO = Point(0, 0, 0)

DIRECTIONS = [NORTH, EAST, SOUTH, WEST, UP, DOWN]
