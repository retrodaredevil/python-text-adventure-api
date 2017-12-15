from abc import abstractmethod, ABC
from enum import Enum, unique, auto
from typing import List, Callable, Optional, TYPE_CHECKING

from textadventure.player import Player
from textadventure.utils import get_unimportant


if TYPE_CHECKING:
    from textadventure.handler import Handler


@unique
class InputHandleType(Enum):  # returned when the InputHandle's handle method/variable property is called
    """
    Most of the time, unless you know the side effects, always use NOT_HANDLED and HANDLED
        HANDLE_AND_DONE    Represents when a response has been handled and should never be responded to again \
                               (Normally use HANDLED) (It won't allow anything to respond at all after this is returned)
    """
    NOT_HANDLED = auto()
    """Used to represent when there was no action taken"""
    HANDLED = auto()
    """Used to represent when there was a noticeable action taken (don't act unless needed after)"""
    PARTIALLY_HANDLED = auto()
    """Used to represent when there was an action taken, but not something too important"""
    UNNOTICEABLE = auto()
    """Used to represent when there was action taken but barely noticeable (should respond to) if returned, \
            and no other responses, it should say Command not recognized."""
    REMOVE_HANDLER = auto()
    """Used to tell the caller of the event to remove the handler(indicates a noticeable action too)"""
    REMOVE_HANDLER_ALLOW_RESPONSE = auto()
    """same as REMOVE_HANDLER but you can respond if you would like (no notic action)"""

    INCORRECT_RESPONSE = auto()
    """Represents when a response was incorrect and the handler doesn't want you to try to use input"""
    HANDLED_AND_DONE = auto()
    """Represents when a response has been handled and should never be responded to again (Normally use HANDLED) \
            (It won't allow anything to respond at all after this is returned)"""

    def should_give_response(self):
        """
        Indicates whether there should be more responses allowed

        :return: True if there are more responses allowed. False if it is advised against that
        """
        # return self is self.__class__.NOT_HANDLED or self is self.__class__.REMOVE_HANDLER_ALLOW_RESPONSE or \
        #     self is self.__class__.UNNOTICEABLE
        return self in [self.__class__.NOT_HANDLED, self.__class__.REMOVE_HANDLER_ALLOW_RESPONSE,
                        self.__class__.UNNOTICEABLE]


class InputObject:
    """
    This object contains a string_input which is the unchanged string that was inputted
    This object also contains the string split up (split_input) which is an array

    Not to be mistaken for PlayerInput, there may be instances in the code where I can an InputObject variable \
        player_input but it's really an InputObject
    """

    def __init__(self, string_input: str):
        self.string_input = string_input
        # DONE actually make this good. I deleted a bunch of this and now it doesn't work. I need to find a better way
        # if you're wondering, this class used to be a lot different.

    def is_empty(self):
        """
        Will almost always return False unless you are handling this InputObject in something like a PlayerOutput\
        because this object should not be passed to methods that are not prepared to handle this.
        Note that you shouldn't try to check this unless you plan to do something if the input is actually empty.

        The implementation of handler doesn't pass this InputObject to InputHandlers if this object returns True,\
        so you won't have to check for this.

        :return: True if the string is empty, False otherwise. (Normally False)
        """
        return len(self.string_input) == 0

    def get_split(self) -> List[str]:
        r = self.string_input.split(" ")
        for element in list(r):
            if not element:
                r.remove(element)
        return r

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

        :param index: The index for the arg. Starts at 0. Using a number less than 0 will produce an unexpected result
        :param ignore_unimportant_before Set to True if you want filter out unimportant words before the argument \
                note that it will never ignore unimportant AFTER the requested index.
        :return: A list of the requested argument and all arguments after it. (Requested arg is in [0])
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
                    if i + 1 in unimportant or s.isspace():  # if the next one is unimportant
                        ignored += 1  # Needed to execute if first if statement again
                    else:  # the next one must be important
                        appending = True
        """
        This method was a pain to write and think about. However, it was worth it because this helps out
        """
        return r

    @staticmethod
    def join(to_join: List[str]) -> str:
        return " ".join(to_join)  # before this line, I wrote about 5 lines. I don't even know python lol


class InputHandler(ABC):
    @abstractmethod
    def on_input(self, handler: 'Handler', player: Player, player_input: InputObject) -> Optional['InputHandle']:
        """
        The reason this doesn't handle the input is because we want all the input handlers to be able to give\
        us their priority and depending on that, we'll call the lower priority number first\
        (lower number higher priority. Explained in InputHandle)

        :param handler: The handler object
        :param player: the player object that gave the input
        :param player_input: The InputObject that contains the string input and other useful data
        :return: An InputHandle that handles the inputs or None if it won't handle the input
        """
        pass

    def _should_handle_input(self, already_handled: List[InputHandleType]) -> bool:
        """
        Should not be called outside of InputHandler or its subclasses
        (should not and is not called in Handler (you must call this on your own in a handle function or not at all))

        :param already_handled: The InputHandleTypes that are already handled
        :return: True if input should be handled in a handle function
        """
        for handle_type in already_handled:
            if not handle_type.should_give_response():
                return False
        return True


class InputHandle:  # returned and used to indicate when the handle function should be called
    def __init__(self, priority: int, handle: Callable[[List[InputHandleType]], InputHandleType],
                 input_handler: InputHandler):
        """
        Note that 0 and 1 should be reserved for client side and to be safe, you shouldn't use 2 or 3 if what you're \
                is not client side only

        :param priority: determines the order to call things in. Lower called first. Ex: 0 then 2 then 10
        :param handle: A function that should return a InputHandleType and should expect a list of InputHandleType
        """
        self.priority = priority
        self.handle = handle
        self.input_handler = input_handler
