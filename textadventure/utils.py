import sys
from difflib import SequenceMatcher
from typing import Union, List, Tuple, TypeVar, Type, Optional, Collection, Iterator

# if TYPE_CHECKING:
#     from textadventure.message import Message


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
Note that the list does not include an empty string ("") because that may mess up stuff.
"""

CanDo = Tuple[bool, MessageConstant]
"""
[0] is a boolean representing if a player can do the action. If [0] is True, then [1] tells why it is True. If\
    False, then [1] is an error message that should be sent to the player. If [0] is True, then [1] is basically debug
If a CanDo from a method was returned, then it is likely that if a player or entity object was passed, no message was\
    sent to them. 
"""


def debug(values):
    """
    Used to debug things

    :param values: The values to print
    """
    print(values, file=sys.stderr)
    sys.stdout.flush()


def error(values):
    """
    Should be used to print errors when raising an exception won't do what you want.

    :param values: The values to print
    """
    debug(values)


def is_string_true(string_input: str):
    return "y" in string_input.lower()


def is_input_valid(string_input: str) -> CanDo:
    """
    :param string_input: The string that the player inputted or a string that may contain unwanted characters
    :return: A CanDo where [0] represents if the string was valid and [1] represents the message that should be sent \
            the player if [0] was False
    """
    for c in string_input:
        if ord(c) not in range(48, 91) and ord(c) not in range(97, 123) and c not in ['_', '-']:
            return False, "You cannot use the character '{}' here."

    return True, "You are able to use that string"


def join_list(to_join: List[str], use_brackets: bool = False, use_indexes: bool = False):
    """
    Creates a string like: Value1, Value2 and Value3. (Lists a list like we do in english)

    :param to_join: The list of strings to join
    :param use_brackets: By default, False, if set to true, instead of using the values of to_join, it will use a '{}'
    :param use_indexes: By default, False, if set to True, the index will be shown before each element in the returned\
        string
    :return: The string that was created
    """
    r = ""
    length = len(to_join)
    for index, s in enumerate(to_join):
        if index > 0:
            if index == length - 1:
                r += " and "
            else:
                r += ", "

        if use_indexes:
            r += "[{}] ".format(index)
        if use_brackets:
            r += "{}"
        else:
            r += s

    return r


T = TypeVar('T')


def get_type_from_list(the_list, allowed_types: Type[T], expected_amount: Optional[int] = None,
                       is_exact_type: bool = False) -> List[T]:
    """
    Helps you get object(s) from a list that are of a certain type along with providing an expected return length of \
    the list to be returned

    :param the_list: The list that you want to grab object(s) from
    :param allowed_types: The type(s) allowed to be returned. Note that this can be a list of types, or just a single\
            type that isn't in a list and is just, well, a type. To keep compatibility, the list type wasn't annotated\
            since putting Type[T] in a Union caused a type error
    :param expected_amount: The expected amount of items in the list that will be returned or None if any length will \
                            be tolerated
    :param is_exact_type: By default False, if True, types will be compared using type(object) == an_allowed_type, \
                            otherwise, types will be compared using using isinstance
    :return: A list of objects from the list that are of a certain type
    """
    def is_type_tolerated(ob) -> bool:
        object_type = type(ob)  # not used unless is_exact_type is True
        for t in allowed_types:
            if (is_exact_type and object_type == t) or (not is_exact_type and isinstance(ob, t)):
                return True

        return False

    if not isinstance(allowed_types, List):  # if the passed object isn't a list, make it one
        # if python supported overloading methods, I would definitely choose that here.
        allowed_types = [allowed_types]
    r = []
    for element in the_list:
        if is_type_tolerated(element):
            r.append(element)
    if expected_amount is not None:
        assert len(r) == expected_amount
    return r


def get_unimportant(to_change: List[str], unimportant_list=NOT_IMPORTANT) -> List[int]:
    """
    Should be used for comparing input to a string. If the input will eventually be outputted, don't print this, \
    you should print the input so the player knows what they actually inputted.

    :param to_change: The list of separated words
    :param unimportant_list: The list of words that are unimportant
    :return: A list of ints where each int corresponds to an index in the to_change list that is unimportant
    """

    r = []
    for index, s in enumerate(to_change):
        test = s
        test = test.lower()
        while test.endswith(".") or test.endswith("!") or test.endswith("?"):
            test = test[:-1]  # removes last character
        if test in unimportant_list:
            r.append(index)

    return r


def are_mostly_equal(a: str, b: str, percent_equal=.8) -> bool:
    """
    Checks to see if the provided strings are mostly equal.
    Converts both to lowercase and removes words from the unimportant list so a: "my the bike" b: "bike" will be True

    :param a: First string
    :param b: Second string
    :param percent_equal: A number from 0 to 1 representing the minimum value of SequenceMatcher#ratio() to return True\
            By default: .8
    :return: True if the strings are mostly equal
    """
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
    return ratio >= percent_equal


class Point:
    def __init__(self, x: int, y: int, z: int = 0):
        """
        Used on locations by having an x, y and z position (z is normally 0)

        :param x: The x position on the map
        :param y: The y position on the map
        :param z: Used for the height/priority (usually 0)
        """
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other: Union['Point', int]):
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
"""Note that the directions should never be compared with 'is' even though they are declared here, you shouldn't\
be doing that"""


T = TypeVar('T')


class TypeCollection(Collection[T]):
    def __init__(self, the_list: List, types_list: List[Type], use_isinstance=True):
        """
        :param the_list: The list of elements that you want to use. Note that changing this list won't affect the one
                in self.the_list because it was initialized using self.the_list = list(the_list)
        :param types_list: The list of types where each time is an acceptable type this is in this Collection
        :param use_isinstance: By default True. If set to False, this will compare types_list using type() instead of
                isinstance()
        """
        self.the_list = list(the_list)
        self.types_list = types_list
        self.use_isinstance = use_isinstance

        self._known_length = None  # simple cache for the __len__ function

    def can_have(self, element):
        for t in self.types_list:
            can = isinstance(element, t) if self.use_isinstance else type(element) == t
            if can:
                return True

        return False

    def __len__(self):
        if self._known_length is not None:
            return self._known_length
        r = 0
        for e in self.the_list:
            if self.can_have(e):
                r += 1
        self._known_length = r
        return self._known_length

    def __contains__(self, x):
        return self.can_have(x) and x in self.the_list

    def __iter__(self):
        return TypeSequenceIterable(self)


class TypeSequenceIterable(Iterator):
    def __init__(self, type_sequence: TypeCollection):
        self.type_sequence = type_sequence
        self.iterator = self.type_sequence.the_list.__iter__()

    def __next__(self):
        n = self.iterator.__next__()
        while not self.type_sequence.can_have(n):
            n = self.iterator.__next__()
        return n


def main():
    my_list = [1., 3, 8, "hello", "cool", 9.0, "c", False, 8]
    seq = TypeCollection(my_list, [str, float, bool])
    for item in my_list:
        print("item: {} is {} in seq".format(item, item in seq))

    print(len(seq))


if __name__ == '__main__':
    main()
