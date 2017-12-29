import warnings
from enum import Enum
from typing import List, TYPE_CHECKING

from textadventure.utils import join_list
from textprint.colors import Color

if TYPE_CHECKING:
    pass


class MessageType(Enum):
    """
    An enum that represents how the message will be printed out and how it will be shown
    """

    IMMEDIATE = 1
    """The message will be printed immediately"""
    TYPED = 2
    """The message will be typed out at normal speed"""
    TYPE_SLOW = 3
    """TYPE_SLOW The message will be typed out slower than the TYPED MessageType"""


class MessagePart:
    """
    A class to represent a small and simple part of a message where all of the text in this part has the same\
    properties.
    """
    DEFAULT_WAIT_BETWEEN = .026

    def __init__(self, main_text: str, print_before="", print_after="", wait_between=DEFAULT_WAIT_BETWEEN,
                 wait_after_print=0):
        """
        Creates a MessagePart with the given attributes. print_before is normally used to change color but if \
                print_before is empty, it's likely that the color has already been changed

        :param main_text: The main text to be printed, should be used for text that will be seen
        :param print_before: Text that will be immediately printed before the main_text, can be used for colors
        :param print_after: Text that will be immediately printed after the main_text, can be used to reset. If this\
                MessagePart contains a new line feed, this is where it should be
        :param wait_between: The wait between each character that is printed in main_text, if 0, main_text should \
                be printed immediately
        :param wait_after_print: Normally 0, but if you just want to pause the output for a moment, change this
        """
        self.main_text = main_text
        self.print_before = print_before
        self.print_after = print_after
        self.wait_between = wait_between
        self.wait_after_print = wait_after_print
        # self.main_text += "'{}'".format(wait_between)


class Message:
    DEFAULT_ENDING = "\n"

    def __init__(self, text: str, message_type: MessageType = MessageType.TYPED, end=DEFAULT_ENDING,
                 wait_in_seconds=0, named_variables: List = None):
        """
        Creates a Message object. All you need is a string to do so.

        If an element in the list named_variables happens to be another list, it should transform each element into a \
        string and call join_list to create a nice string. That list inside the list will only replace ONE {} using\
        join_list

        :param message_type: The MessageType
        :param text: The text
        :param end: What should be put at the end of the string. The ending defaults to \\n
        :param wait_in_seconds: The amount of time in seconds before this prints.
        :param named_variables: A list of variables each overriding __str__ which replaces {} {1} etc\
                                This is recommended because we might want to change the color of something later.
        """
        self.message_type = message_type
        self.text = text
        self.end = end
        self.wait_in_seconds = wait_in_seconds
        if named_variables is None:
            named_variables = []
        self.named_variables = named_variables

    def create_parts(self) -> List[MessagePart]:
        """
        Since messages can be complicated and getting exactly what you want to print can be difficult, we'll split\
            the message into usable MessageParts
        """
        text = self.text
        names = []
        # create the names list (will be similar to self.named_variables)
        for named in self.named_variables:
            if isinstance(named, List):
                names.append(join_list(list(map(str, named))))
                # if you're wonder what the heck the above thing does, don't worry about it. But since you\
                # asked, list(map(str, named)) transforms the list, named, into a list of strings, then\
                # it calls join_list which there is some excellent documentation on that elsewhere. Good day
            else:
                names.append(Color.CYAN >> str(named))  # named could be a string or something that has an __str__ mthd

        try:
            text = text.format(*names)
        except IndexError:
            warnings.warn("Couldn't format to_print: '{}' with names: len:{}, values:{}.".format(text,
                                                                                                 len(names), names))
            warnings.warn("named_variables: len: {}, values: {}".format(len(self.named_variables),
                                                                        self.named_variables))
        text += self.end

        # variable text is now nicely formatted with self.named_variables
        parts = []  # a list of MessageParts
        if self.wait_in_seconds != 0:
            parts.append(MessagePart("", wait_after_print=self.wait_in_seconds))
        wait_between = MessagePart.DEFAULT_WAIT_BETWEEN
        if self.message_type == MessageType.IMMEDIATE:
            wait_between = 0
        current = MessagePart("", wait_between=wait_between)
        # we would have a variable named started here, but instead we can just check if current.main_text is empty
        current_escape = ""  # variable that stores parts of the string that can be added to print_before or print_after
        is_immediate_flag = False  # the char '|' alters whether part of something should be printed immediately
        for c in text:  # go through all the characters
            if len(current_escape) != 0:  # check if there's an escape we are currently appending to and checking
                assert c != chr(27), "Why would we ever have an escape in an escape?"
                # current.main_text += "({})".format(ord(c))
                current_escape += c
                result = Color.get_color(current_escape)
                if isinstance(result, Color):
                    # this is where we add the valid color to the text. In the future, we may add it to a list

                    if len(current.main_text) != 0:
                        the_wait = wait_between if not is_immediate_flag else 0
                        # current.print_after += result.name  # if you want to debug, uncomment
                        # the reason we have this if-else clause, is because if the escape code is RESET, that should\
                        #       go on the end of the MessagePart because that's the best way to represent MessageParts:\
                        #       with RESET codes on print_after and anything else on the print_before of the next MP
                        # In both clauses, we create a new MessagePart because we don't want a MessagePart with \
                        #       multiple escapes on print_after (And it's easy to program this way) (could change later)

                        if result == Color.RESET or result == Color.CLEAR_SECTION:
                            current.print_after += result  # add to print after here
                            parts.append(current)
                            current = MessagePart("", wait_between=the_wait)
                        else:
                            parts.append(current)  # append before since we want to add result to next MessagePart
                            current = MessagePart("", wait_between=the_wait)
                            current.print_before += result  # add to print after here
                    else:
                        # since there's nothing in main_text, we should add this to the beginning
                        current.print_before += result
                    current_escape = ""  # now that we've adding something, we're done with it.
                    continue  # continue if we added something to current
                elif result:  # result should now be a boolean
                    continue  # continue if the char added to current_escape is going to be valid later

            # if we are here, current_escape is invalid or empty already
            current_escape = ""

            # even if the above conditional was True, we still need to run this code. Notice some of the above code\
            #       has continue statements
            if c == chr(27):
                # current.main_text += "(esc)"
                current_escape = c  # yep, it's the same as str(Color.ESCAPE)
            elif c == '\n':
                # if this message has a new line character, add it to the end of a MessagePart
                current.print_after += c
                parts.append(current)
                current = MessagePart("", wait_between=wait_between)
                is_immediate_flag = False  # if there's a new line, we don't really want to carry this
            elif c == '|':  # this character is used to mark part of the text that is printed immediately
                is_immediate_flag = not is_immediate_flag
                parts.append(current)
                current = MessagePart("", wait_between=(wait_between if not is_immediate_flag else 0))
            else:
                # now we should actually add the character to the current since it's a normal character
                current.main_text += c

        # now we are out of the for loop
        if current not in parts and (current.print_before or current.main_text or current.print_after):
            # checks to make sure current isn't in parts and that there's a reason to add it to parts
            """
            Could be the cause of funny behaviour in the future because if there is Something after the NL, that's not
                    in main_text, it will still put it. Depending on how the Message object changes over time, 
                    it might be a good idea to change some of this code and or this if statement
            """
            parts.append(current)

        # parts.append(MessagePart("", print_after=self.end))

        return parts


