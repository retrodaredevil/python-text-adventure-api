from typing import List, Optional, TypeVar, Type, TYPE_CHECKING

from textadventure.action import Action
from textadventure.manager import Manager
from textadventure.player import Player, Living
from textadventure.sending.commandsender import CommandSender
from textadventure.utils import Point, get_type_from_list

if TYPE_CHECKING:
    from textadventure.input.inputhandling import InputHandler, CommandInput, InputHandleType

T = TypeVar("T")


def has_only(the_list: List[T], only_list: List[T]):
    """
    Makes sure that all the items in a list are equal to one of the items in only_list

    :param the_list: The list to check
    :param only_list: The list of acceptable objects to make sure that every weapon in the list is one of these objects
    :return: True if all the items in the list are equal to only, Also True if there are no items in list.
    """
    for ele in the_list:
        if ele not in only_list:
            return False
    return True


class Handler:

    def __init__(self):
        # self.entities = []
        self.identifiables = []
        self.locations = []
        self.input_handlers = []
        """A list of InputHandlers that do not include Locations"""
        self.managers = []
        self.living_things = []
        """A list of livings that normally should never change. It's used to keep track of Living \
        objects which make them easy to retrieve without using a static variable in the class of the living"""

        self.savables = []
        """A Dictionary of savables where the key is something that - this is not completed"""  # TODO

    def start(self):
        """
         Starts the infinite loop for the ninjagame
        """
        while True:
            for player in self.get_players():
                player.update(self)

            for sender in self.get_command_senders():
                inp = sender.take_input()  # this does not pause the thread
                if inp is not None:  # since taking input doesn't pause the thread this could be null
                    self.__do_input(sender, inp)

            for location in self.locations:
                location.update(self)

            for manager in self.managers:
                manager.update(self)

    def __do_input(self, sender: CommandSender, inp: str):
        input_object = CommandInput(inp)
        if sender.player_output.on_input(sender, input_object):
            # since the on_input method returned True, it must have done something, so we don't need to send a message
            return
        if input_object.is_empty():
            # since the player's OutputSender didn't handle this, we should do it
            sender.send_message(
                "You must enter a command. Normally, pressing enter with a blank line won't trigger this.")
            return
        input_handles = []  # Note this is a list of InputHandles
        for input_handler in self.get_input_handlers():
            handle = input_handler.on_input(self, sender, input_object)  # call on_input for each handler
            if handle is not None:
                input_handles.append(handle)

        input_handles.sort(key=lambda k: k.priority)  # sort by priority
        already_handled = []
        for input_handle in list(input_handles):  # copy list so we can delete stuff
            handle_type = input_handle.handle(already_handled)  # note not method # let it decide to take
            assert handle_type is not None, "An InputHandle's handle callable cannot return None. {} broke this rule" \
                .format(type(input_handle.input_handler))  # cannot be None because it said it would handle it

            already_handled.append(handle_type)
            if handle_type is InputHandleType.REMOVE_HANDLER or handle_type is \
                    InputHandleType.REMOVE_HANDLER_ALLOW_RESPONSE:
                self.input_handlers.remove(input_handle.input_handler)
            elif handle_type is InputHandleType.HANDLED_AND_DONE:
                break  # we don't care what others have to say. We're done handling this input

        # player.send_line()  # for the debug
        if len(already_handled) == 0 or has_only(already_handled,
                                                 [InputHandleType.NOT_HANDLED, InputHandleType.UNNOTICEABLE]):
            sender.send_message("Command: \"" + input_object.get_command() + "\" not recognized.")

    def do_action(self, action: Action):
        """
        for each manager in managers call on_action with action

        This method just makes sure all of self.managers's on_action methods are called and does NOTHING ELSE\
        (You must call try_action on your own)

        :param action: The action to be called
        :return: None, but you the action's state should change if one of the managers acted on it
        """
        for manager in self.managers:
            manager.on_action(self, action)

    def get_input_handlers(self) -> List['InputHandler']:
        r = []
        for location in self.locations:
            r.append(location)
            r.extend(location.command_handlers)
        for inp in self.input_handlers:
            r.append(inp)

        return r

    def get_location(self, location_type: type):
        for location in self.locations:
            # print("location's type: " + str(type(location)))
            # print("location_type: " + str(location_type))
            if type(location) is location_type:
                return location
        return None

    def get_players(self) -> List[Player]:
        r = []
        for entity in self.identifiables:
            if isinstance(entity, Player):
                r.append(entity)
        return r

    def get_command_senders(self) -> List[CommandSender]:
        return get_type_from_list(self.identifiables, CommandSender, None)

    def get_managers(self, manager_types: Type[Manager], expected_amount: Optional[int] = None) \
            -> List[Manager]:
        """Quick note, manager_types can be a single type or a list of types. See docs for get_type_from_list"""
        return get_type_from_list(self.managers, manager_types, expected_amount)

    def get_livings(self, living_types: Type[Living], expected_amount: Optional[int] = None) \
            -> List[Living]:
        """Quick note, living_types can be a single type or a list of types. See docs for get_type_from_list"""
        return get_type_from_list(self.living_things, living_types, expected_amount)

    def get_point_location(self, point: Point):
        for location in self.locations:
            if location.point == point:
                return location
        return None
