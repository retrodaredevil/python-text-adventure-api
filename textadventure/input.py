from abc import abstractmethod, ABC
from enum import Enum, unique, auto
from typing import List, Callable, Optional

from textadventure.handler import Handler
from textadventure.player import Player
from textadventure.utils import get_unimportant


@unique
class InputHandleType(Enum):  # returned when the InputHandle's handle method/variableproperty is called
    """
    Most of the time, unless you know the side effects, always use NOT_HANDLED and HANDLED
    Attributes:
        NOT_HANDLED        Used to represent when there was no action taken
        HANDLED            Used to represent when there was a noticeable action taken (don't act unless needed after)
        PARTIALLY_HANDLED  Used to represent when there was an action taken, but not something too important
        RESPONDED_TO       Used to represent when there was action taken but barely noticeable (should respond to)
        REMOVE_HANDLER     Used to tell the caller of the event to remove the handler(indicates a noticeable action too)
        REMOVE_HANDLER_ALLOW_RESPONSE same as REMOVE_HANDLER but you can respond if you would like (no notic action)
        INCORRECT_RESPONSE Represents when a response was incorrect and the handler doesn't want you to try to use input
        HANDLE_AND_DONE    Represents when a response has been handled and should never be responded to again
                                            (Normally use HANDLED)
    """
    NOT_HANDLED = auto()
    HANDLED = auto()
    PARTIALLY_HANDLED = auto()
    RESPONDED_TO = auto()
    REMOVE_HANDLER = auto()
    REMOVE_HANDLER_ALLOW_RESPONSE = auto()
    INCORRECT_RESPONSE = auto()
    HANDLED_AND_DONE = auto()

    def should_give_response(self):
        """
        Indicates whether there should be more responses allowed
        @return: True if there are more responses allowed. False if it is advised against that
        """
        return self is self.__class__.NOT_HANDLED or self is self.__class__.REMOVE_HANDLER_ALLOW_RESPONSE or \
            self is self.__class__.RESPONDED_TO


class InputObject:
    """
    This object contains a string_input which is the unchanged string that was inputted
    This object also contains the string split up (split_input) which is an array

    """

    def __init__(self, string_input: str):
        self.string_input = string_input
        # DONE actually make this good. I deleted a bunch of this and now it doesn't work. I need to find a better way
        # if you're wondering, this class used to be a lot different.

    def get_split(self) -> List[str]:
        return self.string_input.split(" ")

    def get_command_index(self) -> int:
        return 0

    def get_command(self) -> str:
        """
        @return: The name of the command keeping the same case as the input
        """
        return self.get_split()[self.get_command_index()]

    def get_arg(self, index: int, ignore_unimportant_before=True) -> List[str]:
        """
        go to castle of rainbow unicorns
        get_arg(0, True) would return ["castle", "of", "rainbow", "unicorns"]
        get_arg(0, False) would return ["to", "castle", "of", "rainbow", "unicorns"]
        get_arg(1, True) would return ["rainbow", "unicorns"]
        get_arg(1, False) would return ["castle", "of", "rainbow", "unicorns"] note not same as get_arg(0, True)

        Note this should be used to get each arg. (Don't do args = #get_arg(0) and then use that. \
            Use this method multiple times)
        Note that this does not change anything to lower case. Beware when comparing
        @param index: The index for the arg. Starts at 0. Using a number less than 0 will produce an unexpected result
        @param ignore_unimportant_before Set to True if you want filter out unimportant words before the argument
        @return: A list of the requested argument and all arguments after it. (Requested arg is in [0])
        """
        split = self.get_split()
        unimportant: List[int] = []
        if ignore_unimportant_before:
            unimportant = get_unimportant(split)

        start_comparing = self.get_command_index()  # not adding one because once set to True, i will be incremented

        ignored = index
        appending = False  # set to True once ready to start adding to list
        r: List[str] = []
        for i, s in enumerate(split):
            if appending:
                r.append(s)
            else:
                if start_comparing + ignored == i:  # the next one is the request argument
                    if i + 1 in unimportant:  # if the next one is unimportant
                        ignored += 1  # Needed to execute if first if statement again
                    else:  # the next one must be important
                        appending = True
        """
        This method was a pain to write and think about. However, it was worth it because this helps out
        """
        return r

    @staticmethod
    def join(to_join: List[str]) -> str:
        r = ""
        for s in to_join:
            r += s
            r += " "
        r = r[:-1]
        return r


class InputHandler(ABC):
    @abstractmethod
    def on_input(self, handler: 'Handler', player: 'Player', player_input: InputObject) -> Optional['InputHandle']:
        """
        The reason this doesn't handle the input is because we want all the input handlers to be able to give\
        us their priority and depending on that, we'll call the lower priority number first\
        (lower number higher priority. Explained in InputHandle)
        @param handler: The handler object
        @type handler: 'Handler'
        @param player: the player object that gave the input
        @param player_input: The InputObject that contains the string input and other useful data
        @rtype: Optional[InputHandle]
        @return: An InputHandle that handles the inputs or None if it won't handle the input
        """
        pass

    def _should_handle_input(self, already_handled: List[InputHandleType]) -> bool:
        """
        Should not be called outside of InputHandler or its subclasses
        (should not and is not called in Handler (you must call this on your own in a handle function or not at all))
        @param already_handled: The InputHandleTypes that are already handled
        @return: True if input should be handled in a handle function
        """
        for handle_type in already_handled:
            if not handle_type.should_give_response():
                return False
        return True


class InputHandle:  # returned and used to indicate when the handle function should be called
    def __init__(self, level: int, handle: Callable[[List[InputHandleType]], InputHandleType],
                 input_handler: InputHandler):
        """
        @param level: determines the order to call things in. Lower called first. Ex: 0 then 2 then 10
        @param handle: A function that should return a InputHandleType and should expect a list of InputHandleType
        """
        self.level = level
        self.handle = handle
        self.input_handler = input_handler
