from abc import abstractmethod, ABC
from enum import Enum, unique
from typing import List, Callable, Optional, TYPE_CHECKING, Dict, Union, Tuple

from textadventure.player import Player
from textadventure.sending.commandsender import CommandSender
from textadventure.utils import get_unimportant
import shlex

if TYPE_CHECKING:
    from textadventure.handler import Handler


FlagOptions = Dict[Tuple[str, ...], Optional[int]]
"""A dictionary where each key is a tuple of strings that represent a single flag. Each value is the number of
arguments each flag should have. Usually 0 for most flags (True and False) but sometimes 1 for something like --file
and rarely more than 1. If the value is None, then the flag takes up the rest of the command"""


@unique
class InputHandleType(Enum):  # returned when the InputHandle's handle method/variable property is called
    """
    Most of the time, unless you know the side effects, always use NOT_HANDLED and HANDLED
        HANDLE_AND_DONE    Represents when a response has been handled and should never be responded to again \
                               (Normally use HANDLED) (It won't allow anything to respond at all after this is returned)
    """
    NOT_HANDLED = 1
    """Used to represent when there was no action taken"""
    HANDLED = 2
    """Used to represent when there was a noticeable action taken (don't act unless needed after)"""
    PARTIALLY_HANDLED = 3
    """Used to represent when there was an action taken, but not something too important"""
    UNNOTICEABLE = 4
    """Used to represent when there was action taken but barely noticeable (should respond to) if returned, \
            and no other responses, it should say Command not recognized."""
    REMOVE_HANDLER = 5
    """Used to tell the caller of the event to remove the handler(indicates a noticeable action too)"""
    REMOVE_HANDLER_ALLOW_RESPONSE = 6
    """same as REMOVE_HANDLER but you can respond if you would like (no notic action)"""

    INCORRECT_RESPONSE = 7
    """Represents when a response was incorrect and the handler doesn't want you to try to use input"""
    HANDLED_AND_DONE = 8
    """Represents when a response has been handled and should never be responded to again (Normally use HANDLED) \
            (It won't allow anything to respond at all after this is returned)"""
    UNSUPPORTED_SENDER = 9
    """Represents when there was no action taken because whatever was sending the command is unable to perform it.
    This is not recommended every time since sometimes you will want to tell the sender that they can't perform it.
    However, if you are NOT going to tell them, you should return this instead of NOT_HANDLED"""

    def should_give_response(self):
        """
        Indicates whether there should be more responses allowed

        :return: True if there are more responses allowed. False if it is advised against that
        """
        # return self is self.__class__.NOT_HANDLED or self is self.__class__.REMOVE_HANDLER_ALLOW_RESPONSE or \
        #     self is self.__class__.UNNOTICEABLE
        return self in [self.__class__.NOT_HANDLED, self.__class__.REMOVE_HANDLER_ALLOW_RESPONSE,
                        self.__class__.UNNOTICEABLE, self.__class__.UNSUPPORTED_SENDER]


class CommandInput:
    """
    This object contains a string_input which is the unchanged string that was inputted
    This object also contains the string split up (split_input) which is an array

    Also, this uses shlex.split so a command like: "command_name 'cool string' space\ string" gives 3 parts. 1 command,
    2 args
    """

    def __init__(self, string_input: str):
        self._string_input = string_input
        try:
            self._split = self.__class__.do_split(string_input)
        except ValueError as e:
            self._split = string_input.split(" ")
            self.input_error = e
        else:
            self.input_error = None
            """
            If the parser had trouble parsing the input. (Ex: There's no closing quote) this will be a ValueError
            where input_error.args[0] is the error as a string. If this is not None, then that means that split() will 
            return a list of strings split only by spaces (not using unix like parsing).
            """

    def __str__(self):
        return self._string_input

    def is_empty(self):
        """
        Will almost always return False unless you are handling this CommandInput in something like a OutputSender\
        because this object should not be passed to methods that are not prepared to handle this.
        Note that you shouldn't try to check this unless you plan to do something if the input is actually empty.

        The implementation of handler doesn't pass this CommandInput to InputHandlers if this object returns True,\
        so you won't have to check for this.

        :return: True if the string is empty, False otherwise. (Normally False)
        """
        return len(self.split()) == 0

    def split(self) -> List[str]:
        return self._split

    def get_command_index(self) -> int:
        """
        A simple method that for now, returns 0 but should always be used because having another simple layer of \
            abstraction is never a bad idea
        """
        return 0

    def get_command(self) -> str:
        """
        :return: The name of the command keeping the same case as the input
        """
        return self.split()[self.get_command_index()]

    def get_arg(self, index: int, ignore_unimportant_before=True,
                flag_options: Optional[FlagOptions] = None) -> List[str]:
        """
        go to castle of rainbow unicorns
        get_arg(0, True) would return ["castle", "of", "rainbow", "unicorns"]
        get_arg(0, False) would return ["to", "castle", "of", "rainbow", "unicorns"]
        get_arg(1, True) would return ["rainbow", "unicorns"]
        get_arg(1, False) would return ["castle", "of", "rainbow", "unicorns"] note not same as get_arg(0, True)

        Note this should be used to get each arg. (Don't do args = #get_arg(0) and then use that. \
        Use this method multiple times)

        Note that this does not change anything to lower case. Beware when comparing

        :param index: The index for the arg. Starts at 0. Using a number less than 0 will produce an unexpected result
        :param ignore_unimportant_before Set to True if you want filter out unimportant words before the argument \
                note that it will ALWAYS ignore unimportant AFTER the requested index.
        :param flag_options: The dict representing the flag options. This is used to ignore flags in the returned list.
                             If set to None (default), then it will assume that all flags have 0 arguments after them
                             essentially only ignoring the flags themselves. If it is not None, then it will only
                             ignore flags specified in the dict itself.

                             If this is an empty dict, then that essentially makes it so flags are not ignored
                             and can be in the returned list.

                             Note that flags after the first argument are not treated as flags ex:
                             "command_name my_arg --my_flag" --my_flag is always treated as an argument
        :return: A list of the requested argument and all arguments after it. (Requested arg is in [0]) You are allowed
                 to change (remove/append) to the returned list
        """
        split = self.split()  # get the command args into split parts
        unimportant = []  # a list of ints representing the unimportant words in a string where each is an index
        if ignore_unimportant_before:
            unimportant = get_unimportant(split)

        start_comparing = self.get_command_index()  # not adding one because once set to True, i will be incremented
        #       note that the value above is normally 0 because that's where the command is

        ignored = index
        appending = False  # set to True once ready to start adding to list
        r = []
        for i, s in enumerate(split):
            if appending:  # once we start appending, we never stop
                r.append(s)
            else:
                is_next_flag = False
                if len(split) > i + 1:  # entire if statement is to check for flags
                    next_arg = split[i + 1]
                    flags = self.__class__.parse_flag(next_arg)
                    if flags is not None:
                        if len(flags) > 1:  # assume that there are 0 arguments after something like -al
                            is_next_flag = all(FlagData.get_option(flag, flag_options) is not None for flag in flags)
                        else:
                            option = FlagData.get_option(flags[0], flag_options)
                            if option is not None:
                                aliases, num_flag_args = option
                                is_next_flag = True  # 1 will be added to ignored anyway
                                ignored += num_flag_args
                                # TODO fix side effect where if next arg is flag it still increments ignored
                    if is_next_flag:
                        ignored += 1
                if start_comparing + ignored == i:  # the next one is the request argument
                    # assert not s.isspace()
                    if i + 1 in unimportant:
                        # basically what this does, if we are ignoring this arg, add 1 to ignored so we will get
                        # one arg to the right
                        ignored += 1  # Needed to execute if first if statement again
                    else:  # the next one must be important
                        appending = True
        """
        This method was a pain to write and think about. However, it was worth it because this helps out
        """
        return r

    def subcommand(self, index=0, ignore_unimportant_before=True) -> 'CommandInput':
        """
        Creates another CommandInput that you can treat just like you would a regular command, except it's for a sub
        command. Each argument is optional and normally they should not be changed

        :param index: The argument index that you want to be the main command for the CommandInput that is returned
        :param ignore_unimportant_before: If True, this will filter out unimportant arguments that are before or include
                                          index
        :return: A CommandInput where the main command is the argument specified by index (normally 0)
        """
        return CommandInput(self.__class__.join(self.get_arg(index, ignore_unimportant_before)))

    def get_flags(self, ignore_unimportant_before=True, allow_flags_after_args=False, ignore_command=True) -> List[str]:
        """
        :param ignore_unimportant_before: If allow_flags_after_args is False, this says whether or not unimportant
                                          words should be counted as args
        :param allow_flags_after_args: If False, then flags after the first argument will not be returned
        :param ignore_command: Normally True. If set to False, and the command is a flag, it will also return that
        :return: The flags of this command as a list of strings. You are allowed to change (remove/append) to the
                 returned list
        """
        flags = []
        split = self.split()
        if ignore_unimportant_before:
            unimportant = get_unimportant(split)
        else:
            unimportant = []

        start_comparing = self.get_command_index()

        for i, arg in enumerate(split):
            if i > start_comparing or not ignore_command:  # make sure it isn't the command
                flag = self.__class__.parse_flag(arg)
                if flag is not None:
                    flags.extend(flag)
                elif i not in unimportant and not allow_flags_after_args:
                    break

        return flags

    # def get_arg_flag(self):

    @staticmethod
    def parse_flag(arg: str) -> Optional[List[str]]:
        """
        Examples:

        "-h" -> ["h"]
        "-hs" -> ["h", "s"]

        "--help" -> ["help"]

        "--" -> None

        "hi" -> None


        :param arg: The argument to parse the flag for
        :return: A list of one flag or a list of multiple, single character flags, or None if there was no flag
        """
        length = len(arg)

        if length < 2:
            return None

        if arg[0] == '-':
            if arg[1] == '-':
                if length > 2:  # there's no flag "--"
                    return [arg[2:]]
            else:  # -a -ab -abc
                return list(arg[1:])

        return None

    @staticmethod
    def join(to_join: List[str]) -> str:
        """
        If you have a list of arguments or something like that from a CommandInput, this is the recommended way of
        reconstructing that into a string

        :param to_join:
        :return:
        """
        return " ".join(shlex.quote(part) for part in to_join)

    @staticmethod
    def do_split(to_split: str) -> List[str]:
        return shlex.split(to_split)


class FlagData:
    def __init__(self, command: CommandInput, flag_options: FlagOptions):
        self.command = command
        self.flag_options = flag_options

    @staticmethod
    def get_option(flag_name: str, flag_options: Optional[FlagOptions]) -> Optional[Tuple[Tuple[str], int]]:
        """

        :param flag_name: The name of the flag which may have multiple aliases
        :param flag_options: The FlagOptions dict where each key is a tuple of aliases/names and each value is the
                             number of arguments that come after the flag represented by the names

                             If this is None, then the returned value will be (flag_name,), 0 meaning that by default,
                             this allows you to have no flag_options making things assume every flag is valid and
                             has no arguments after it. Use this carefully.
        :return: A tuple where [0] is a tuple representing all the aliases/names of the flag. [1] is an int
                 representing the number of arguments that come after the flag usually 0, sometimes 1, rarely > 1
        """
        if flag_options is None:
            return (flag_name,), 0
        try:
            # thanks: https://stackoverflow.com/a/2974082
            return next((k, v) for k, v in flag_options.items() if flag_name in k)
        except StopIteration:
            return None

    def get_flag(self, name) -> Union[bool, Optional[str], Optional[List[str]]]:
        """
        :param name: The name of the flag.
        :return: If the value corresponding with the name is 0 (0 arguments) then the return value will be a bool
                 that is True if the name (or any aliases) are in command.get_flags().

                 If the value is 1, then the return value will be: a string representing the argument that came after
                 the flag. If the flag was not in the command it will return None.
                 However, if it was in the command and there was no argument after it, it will return an empty string.

                 If the value is greater than 1, then the return value will be a list of strings with a max length of
                 the value from flag_options. If the flag was not present in the command, it will return None.
                 However,
                 if there were no arguments or there were less than <value> amount of arguments after it then the length
                 of the returned list may not be value
        """
        option = self.__class__.get_option(name, self.flag_options)
        if option is None:
            raise ValueError("Was unable to find flag: '{}' in flag_options: {}".format(name, self.flag_options))
        aliases, num_args = option

        if num_args == 0:
            return any(flag in aliases for flag in self.command.get_flags())

        r = []
        append = False
        for arg in self.command.split():
            if append:
                r.append(arg)
                if len(r) == num_args:
                    break
                continue

            flags = CommandInput.parse_flag(arg)
            if flags is not None and any(alias in flags for alias in aliases):
                append = True
                if len(flags) > 1:
                    break  # if there are multiple flags like: -asdf then return an empty list or empty string

        if not append:  # flag was not present in command
            return None
        if num_args == 1:
            return r[0] if len(r) > 0 else ""
        return r


class InputHandler(ABC):
    @abstractmethod
    def on_input(self, handler: 'Handler', sender: CommandSender, command_input: CommandInput) -> \
            Optional['InputHandle']:
        """
        The reason this doesn't handle the input is because we want all the input handlers to be able to give\
        us their priority and depending on that, we'll call the lower priority number first\
        (lower number higher priority. Explained in InputHandle)

        :param handler: The handler object
        :param sender: the CommandSender object that gave the input
        :param command_input: The CommandInput that contains the string input and other useful data
        :return: An InputHandle that handles the inputs or None if it won't handle the input
        """
        pass

    def _should_handle_input(self, already_handled: List[InputHandleType]) -> bool:
        """
        Should not be called outside of InputHandler or its subclasses
        (should not and is not called in Handler (you must call this on your own in a handle function or not at all))

        Just to be clear, this is only called in subclasses of InputHandler making this a 'protected' method

        The reason that that method is optional to call, is that the default method just checks to see if \
        any of the InputHandleTypes in already_handled return False indicating that someone doesn't want you to try\
        to handle the input since they already did it. This method just checks that and you may want to handle the \
        command still.

        Since you don't have the already_handled list when on_input is called, you call this when the function you\
        passed to InputHandle is called. (One of the arguments of that includes already_handled which you should then\
        pass to this method)

        :param already_handled: The InputHandleTypes that are already handled
        :return: True if input should be handled in a handle function
        """
        for handle_type in already_handled:
            if not handle_type.should_give_response():
                return False
        return True


class PlayerInputHandler(InputHandler):
    def on_input(self, handler: 'Handler', sender: CommandSender, command_input: CommandInput):
        """
        By default, checks if the sender variable is an instance of a Player, if it is, call and return \
        on_player_input. Otherwise, return None
        """
        if isinstance(sender, Player):
            return self.on_player_input(handler, sender, command_input)
        return None

    @abstractmethod
    def on_player_input(self, handler: 'Handler', player: Player, command_input: CommandInput) -> \
            Optional['InputHandle']:
        """
        Does the same thing as :func:`~inputhandling.InputHandler.on_input`
        """
        pass


class InputHandle:  # returned and used to indicate when the handle function should be called
    PRIORITY_LOW = 12
    """Priority that is lower than PRIORITY_LOCATION."""
    PRIORITY_LOCATION = 10
    """Priority that should be used for almost all locations that handle commands"""

    PRIORITY_COMMAND = 8
    """Priority that should be used for almost all commands"""
    PRIORITY_COMMAND_ALIAS = 7
    """Priority that should be used for some commands. It is a higher priority than PRIORITY_COMMAND"""
    PRIORITY_UNINTERRUPTED = 6
    """Priority that should be used for custom parts. (Maybe a NameTaker or an options menu)"""
    PRIORITY_COMMAND_HIGH = 5
    """Priority that almost guarantees this will be handled first. (Although client side stuff will be handled first)"""

    PRIORITY_CLIENT = 1
    """Should be used for most client side commands that you don't want going to the server. One of the highest
    priorities"""
    PRIORITY_CLIENT_HIGH = 0
    """Should be used if you are making something that you don't want anything else to handle. Highest priority"""

    def __init__(self, priority: int, handle: Callable[[List[InputHandleType]], InputHandleType],
                 input_handler: InputHandler):
        """
        Note that 0 and 1 should be reserved for client side and to be safe, you shouldn't use 2 or 3 if what you're
        is not client side only

        :param priority: determines the order to call things in. Lower called first. Ex: 0 then 2 then 10. Note it is\
                recommended to use the class variables provided by using InputHandle.PRIORITY_<needed priority here>
        :param handle: A function that should return a InputHandleType and should expect a list of InputHandleType
        """
        self.priority = priority
        self.handle = handle
        self.input_handler = input_handler
