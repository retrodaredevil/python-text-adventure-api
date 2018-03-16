from pyparsing import Literal, nums, Word, delimitedList, Optional, alphas, oneOf, Combine, Suppress

# note this imports a class called Optional. If we, in the future, import typing.Optional, this will conflict


ESC = Literal("\x1b")
integer = Word(nums)
escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer, ';')) + oneOf(list(alphas)))


# thanks https://stackoverflow.com/questions/2186919
def strip_ansi(to_strip: str):
    return Suppress(escapeSeq).transformString(to_strip)


def length_without_ansi(the_string):
    """
    Gets the length of a string as it would be in a terminal (without ansi sequences)
    This method uses the strip_ansi method, but this method is recommended only if you want to get the length

    Also note, this method takes a lot more time than len(the_string)

    :param the_string: The string to get the length of without counting ansi escape sequences
    :return: The length of the string not counting ansi escape sequences
    """
    return len(strip_ansi(the_string))

