from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List


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


class MessagePart:  # work in progress
    def __init__(self, main_text: str, print_before="", print_after="", wait_between=.2):
        """
        Creates a MessagePart with the given attributes. print_before is normally used to change color but if \
                print_before is empty, it's likely that the color has already been changed

        :param main_text: The main text to be printed, should be used for text that will be seen
        :param print_before: Text that will be immediately printed before the main_text, can be used for colors
        :param print_after: Text that will be immediately printed after the main_text, can be used to reset
        :param wait_between: The wait between each character that is printed in main_text, if 0, main_text should \
                be printed immediately
        """
        self.main_text = main_text
        self.print_before = print_before
        self.print_after = print_after
        self.wait_between = wait_between


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
        self.ending = end
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
        pass


class PlayerInput(ABC):
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

