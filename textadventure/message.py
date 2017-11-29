import warnings
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, TYPE_CHECKING

from textadventure.utils import join_list
from textprint.colors import Color

if TYPE_CHECKING:
    from textadventure.player import Player
    from textadventure.inputhandling import InputObject


class MessageType(Enum):
    """
    An enum that represents how the message will be printed out and how it will be shown

    Attributes:
        IMMEDIATE The message will be printed immediately
        TYPED     The message will be typed out at normal speed
        WAIT      The message will be typed out immediately accept when there's a lew line character,
                    it will wait before printing that out. Also should be used when sending a wait between messages
        TYPE_SLOW The message will be typed out slower than the TYPED MessageType

    """

    IMMEDIATE = auto()
    TYPED = auto()
    TYPE_SLOW = auto()


class MessagePart:
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
        self.named_variables: List = named_variables

    def create_parts(self) -> List[MessagePart]:
        """
        Since messages can be complicated and getting exactly what you want to print can be difficult, we'll split\
            the message into usable MessageParts

        :return:
        """
        text = self.text
        names: List[str] = []  # noinspection PyTypeChecker
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
        parts: List[MessagePart] = []
        wait_between = MessagePart.DEFAULT_WAIT_BETWEEN
        if self.message_type == MessageType.IMMEDIATE:
            wait_between = 0
        current = MessagePart("", wait_between=wait_between)
        # we would have a variable named started here, but instead we can just check if current.main_text is empty
        done = False  # are we done concatenating text to current.main_text
        current_escape = ""  # variable that stores parts of the string that can be added to print_before or print_after
        for c in text:  # go through all the characters
            if len(current_escape) != 0:  # check if there's an escape we are currently appending to and checking
                current_escape += c
                result = Color.get_color(current_escape)
                if isinstance(result, Color):
                    # this is where we add the valid color to the text. In the future, we may add it to a list
                    if len(current.main_text) != 0:
                        if result == Color.RESET:
                            current.print_after += result
                            parts.append(current)
                            current = MessagePart("")
                        else:
                            parts.append(current)  # append before since
                            current = MessagePart("")
                            current.print_after += result
                    else:
                        current.print_before += result
                    continue  # continue if we added something to current
                elif result:
                    continue  # continue if the char added to current_escape is going to be valid later
                else:
                    # if this else fired, it means that the current_escape is not invalid and we should reset it
                    current_escape = ""  # it will be reset anyway (below), but this makes the code more understandable
                    # later, if the code below is changed, we should make sure to reset it

            # even if the above conditional was True, we still need to run this code. Notice some of the above code\
            #       has continue statements
            if c == str(Color.ESCAPE):
                current_escape = c  # yep, it's the same as str(Color.ESCAPE)
            elif c == '\n':
                # if this message has a new line character, add it to the end of a MessagePart
                current_escape = ""
                current.print_after += c
                parts.append(current)
                current = MessagePart("")
            else:
                current_escape = ""  # if we made it here, whatever was in current_escape is either invalid or has\
                #       already been added as a color
                if done:  # stuff has been added to all three
                    parts.append(current)
                    current = MessagePart("")
                # now we should actually add the character to the current since it's a normal character
                current.main_text += c

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


class PlayerInputGetter(ABC):
    @abstractmethod
    def take_input(self) -> str:
        """
        :return: a string representing the input or None
        Calling this method should not make the current thread sleep
        """
        pass

        # @abstractmethod  Commented out because it's not really used at all
        # def set_input_prompt(self, message: str):
        #     """
        #     Sets the input prompt
        #     :param message: The string to set the input prompt to
        #     :return: None
        #     """
        #     pass


class PlayerOutput(ABC):
    @abstractmethod
    def send_message(self, message: Message):
        """
        :param message: the message to send
        """
        pass

    def on_input(self, player: 'Player', player_input: 'InputObject') -> bool:
        """
        By default, this method returns False the string is empty. Subclasses of PlayerOutput may change this.
        And if they do change the implementation, they should check if player_input.is_empty() or call super.

        Note that if this method returns False, no message is sent to the player so you should send a message to the \
        player or do something like speeding up text. (Different implementations can handle this differently)

        :param player: The player that this PlayerOutput is attached to
        :param player_input: The input that the player typed. Notice that the method is_empty() could return True
        :return: True if you want to cancel the handling/sending of the input. False otherwise (Normally False)
        """
        if player_input.is_empty():
            player.send_message("You entered an empty line.")
            return True
        return False
