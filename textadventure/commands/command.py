from abc import abstractmethod
from typing import List

from textadventure.entity import Entity
from textadventure.handler import Handler
from textadventure.input.inputhandling import InputHandler, CommandInput, InputHandle, InputHandleType
from textadventure.location import Location
from textadventure.sending.commandsender import CommandSender


class CommandHandler(InputHandler):
    """
    A CommandHandler object represents an InputHandler's ability to handle a command in a certain way
    An
    """

    def __init__(self):
        pass

    def on_input(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        if not self._should_handle_sender(sender) or not self._should_handle_command(command_input):
            return None

        def handle_function(already_handled: List[InputHandleType]):
            if not self._should_handle_input(already_handled):
                return InputHandleType.NOT_HANDLED
            first_arg = command_input.get_arg(0, False)
            if "help" in command_input.get_flags() or (len(first_arg) != 0 and first_arg[0].lower() == "help"):
                self.send_help(sender)
                return InputHandleType.HANDLED
            return self._handle_command(handler, sender, command_input)

        return InputHandle(InputHandle.PRIORITY_COMMAND, handle_function, self)

    @abstractmethod
    def send_help(self, sender: CommandSender):
        """
        Called inside from the handle_function in on_input and passed through the InputHandle returned by on_input

        By default, the on_input method will call this method if the first argument of the command is equal to "help"
        so even if you don't call this in your overridden _handle_command, it can still be called.
        """
        pass

    @abstractmethod
    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput) -> InputHandleType:
        """
        The _ means that this method is meant to be "protected" and should only be called within classes and subclasses
        should not be called outside of CommandHandler

        Obviously, since this is abstract, it should be overridden by subclasses. This is where your main command code
        goes

        :param handler: The handler object
        :param sender:  The player object
        :param command_input: The player's input
        :return: An InputHandleType that will be returned by the handle Callable in InputHandle
        """
        pass

    @abstractmethod
    def _should_handle_command(self, command_input: CommandInput) -> bool:
        """
        Overridden by subclasses of CommandHandler and returns whether or not a command should be handled
        Called in on_input
        Should not be called in places other than the CommandHandler class

        :param command_input:
        :return: returns True if a command should be handled (even if argsuments are incorrect)
        """
        pass

    def _should_handle_sender(self, sender: CommandSender) -> bool:
        """
        Tells whether or not a certain command will have an effect for a sender(Normally returns true unless overridden)
        called in on_input
        Called by the CommandHandler class and doesn't ever need to be called on your own. Feel free to override

        :param sender: The sender to check
        :return: A boolean, True if this command should handle a player False otherwise
        """
        return True


# noinspection PyAbstractClass
class SimpleCommandHandler(CommandHandler):
    def __init__(self, command_names: List[str], description):
        """
        A subclass of CommandHandler that makes using/extending CommandHandler simpler

        :param command_names: A list of strings that will trigger this command
        :param description: The help/description string
        """
        super(SimpleCommandHandler, self).__init__()
        self.command_names = command_names
        self.description = description

    def _should_handle_command(self, command_input: CommandInput):
        return command_input.get_command().lower() in self.command_names

    def send_help(self, sender: CommandSender):
        sender.send_message(self.description)


# noinspection PyAbstractClass
class LocationCommandHandler(SimpleCommandHandler):
    def __init__(self, command_names: List[str], description, location: Location):
        """
        :param location: The specific location to handle or None to handle all locations
        """
        super(LocationCommandHandler, self).__init__(command_names, description)
        self.location = location

    def _should_handle_sender(self, sender: CommandSender) -> bool:
        """
        :return: return self.location is None or player.location == self.location
        """
        return self.location is None or (isinstance(sender, Entity) and sender.location == self.location)
