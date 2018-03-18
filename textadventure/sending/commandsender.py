from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from textadventure.sending.message import Message, MessageType
from textadventure.utils import MessageConstant
from textprint.colors import Color

if TYPE_CHECKING:
    from textadventure.input.inputhandling import CommandInput


class InputGetter(ABC):
    @abstractmethod
    def take_input(self) -> Optional[str]:
        """
        Calling this method should not make the current thread sleep
        :return: a string representing the input or None
        """
        pass


class OutputSender(ABC):
    @abstractmethod
    def send_message(self, message: Message):
        """
        :param message: the message to send
        """
        pass

    def on_input(self, sender: 'CommandSender', command_input: 'CommandInput') -> bool:
        """
        By default, this method returns False. Subclasses of OutputSender may change this.
        And if they do change the implementation, they should check if input_getter.is_empty() or call super.

        Note that if this method returns False, no message is sent to the player so you should send a message to the \
        player or do something like speeding up text. (Different implementations can handle this differently)

        :param sender: The CommandSender that this OutputSender is attached to
        :param command_input: The input that the player typed. Notice that the method is_empty() could return True
        :return: True if you want to cancel the handling/sending of the input. False otherwise (Normally False)
        """
        if command_input.is_empty():
            sender.send_message("You entered an empty line.")
            return True
        return False


class CommandSender:

    def __init__(self, input_getter: InputGetter, output: OutputSender):
        self.input_getter = input_getter
        self.output = output

    def send_message(self, message):
        self.output.send_message(self.get_message(message))

    def send_wait(self, seconds):
        self.output.send_message(Message("", end="", wait_in_seconds=seconds))

    def send_line(self, amount: int = 1):
        ending = Message.DEFAULT_ENDING
        if amount != 1:
            ending = ""
            for i in range(0, amount):
                ending += Message.DEFAULT_ENDING
        self.send_message(Message("", MessageType.IMMEDIATE, end=ending))

    def clear_screen(self):
        self.send_message(str(Color.CLEAR_SECTION))

    def take_input(self) -> Optional[str]:
        """
        Once this method is called, the returned value will not be returned again (unless typed again)

        This method should only be called in one place. If this is called repeatedly, only one caller will get the info

        :return: a string or None if there is no input to take
        """
        return self.input_getter.take_input()

    @staticmethod
    def get_message(message: MessageConstant) -> Message:
        """
        Converts a MessageConstant to a Message
        Makes sure that the passed message value is returned as a Message object

        :param message: The message or string to make sure or change to a Message
        :return: A message object
        """

        if type(message) is str:
            message = Message(message)
        if type(message) is not Message:
            raise TypeError("The type: " + str(type(message)) + " is not supported")
        return message

