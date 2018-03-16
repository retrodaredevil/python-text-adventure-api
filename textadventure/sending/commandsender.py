from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from textadventure.sending.message import Message, MessageType
from textadventure.utils import MessageConstant
from textprint.colors import Color

if TYPE_CHECKING:
    from textadventure.input.inputhandling import CommandInput


class InputGetter(ABC):
    @abstractmethod
    def take_input(self) -> str:
        """
        Calling this method should not make the current thread sleep
        :return: a string representing the input or None
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
        And if they do change the implementation, they should check if command_input.is_empty() or call super.

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

    def __init__(self, command_input: InputGetter, player_output: OutputSender):
        self.command_input = command_input
        self.player_output = player_output

    def send_message(self, message):
        self.player_output.send_message(self.get_message(message))

    def send_wait(self, seconds):
        self.player_output.send_message(Message("", end="", wait_in_seconds=seconds))

    def send_line(self, amount: int = 1):
        ending = Message.DEFAULT_ENDING
        if amount != 1:
            ending = ""
            for i in range(0, amount):
                ending += Message.DEFAULT_ENDING
        self.send_message(Message("", MessageType.IMMEDIATE, end=ending))

    def clear_screen(self):
        self.send_message(str(Color.CLEAR_SECTION))

    def take_input(self) -> str:
        """
        Once this method is called, the returned value will not be returned again (unless typed again)

        :return: a string or None if there is no input to take
        """
        return self.command_input.take_input()

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

