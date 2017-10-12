from typing import List, Optional, TypeVar

from textadventure.action import Action
from textadventure.entity import Entity
from textadventure.manager import Manager
from textadventure.message import Message, MessageType, StreamOutput
from textadventure.player import Player, Living
from textadventure.utils import Point

T = TypeVar("T")


def has_only(the_list: List[T], only_list: List[T]):
    """
    Makes sure that all the items in a list are equal to one of the items in only_list
    @param the_list: The list to check
    @param only_list: The list of acceptable objects to make sure that every item in the list is one of these objects
    @return: True if all the items in the list are equal to only, Also True if there are no items in list.
    """
    for ele in the_list:
        if ele not in only_list:
            return False
    return True


class Handler:
    """
    Attributes:
        input_handlers    Input handlers that do not include locations
        living_things     A list of livings that normally should never change. It's used to keep track of Living \
                                objects which make them easy to retrieve without using a static variable in the class\
                                of the living
    """

    def __init__(self):
        from textadventure.location import Location
        from textadventure.input import InputHandler
        self.entities: List[Entity] = []
        self.locations: List[Location] = []
        self.input_handlers: List[InputHandler] = []
        self.managers: List[Manager] = []
        self.living_things: List[Living] = []

    def start(self):
        """
         Starts the infinite loop for the ninjagame
        """
        while True:
            for player in self.get_players():
                player.update(self)
                inp = player.take_input()  # this does not pause the thread
                if inp is not None:  # since taking input doesn't pause the thread this could be null
                    self.__do_input(player, inp)

            for location in self.locations:
                location.update(self)

            for manager in self.managers:
                manager.update(self)

    def __do_input(self, player: Player, inp: str):
        from textadventure.input import InputObject, InputHandleType
        input_object = InputObject(inp)
        input_handles: List[InputHandle] = []
        for input_handler in self.get_input_handlers():
            handle = input_handler.on_input(self, player, input_object)  # call on_input for each handler
            if handle is not None:
                input_handles.append(handle)

        input_handles.sort(key=lambda k: k.level)  # sort by level
        already_handled: List[InputHandleType] = []
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
            player.send_message("Command: \"" + input_object.get_command() + "\" not recognized.")

    def do_action(self, action: Action):
        """
        for each manager in managers call on_action with action
        This method just makes sure all of self.managers's on_action methods are called and does NOTHING ELSE\
            (You must call try_action on your own)
        @param action: The action to be called
        @return: None, but you the action's state should change if one of the managers acted on it
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
        for entity in self.entities:
            if isinstance(entity, Player):
                r.append(entity)
        return r

    def get_livings(self, living_type: type, expected_amount: Optional[int] = None) -> List[Living]:
        """
        Returns a list of Living with the type living_type
        @param living_type: The type to get
        @param expected_amount: The expected length of the list that will be returned. \
                                    If not None, assert len(the list) == expected_amount
        @return: A list of Living with the type living_type
        """
        r = []
        for living in self.living_things:
            if type(living) is living_type:
                r.append(living)
        if expected_amount is not None:
            assert len(r) == expected_amount
        return r

    def get_point_location(self, point: Point):
        for location in self.locations:
            if location.point == point:
                return location
        return None


from textadventure.input import InputHandler, InputObject, InputHandleType, InputHandle


class SettingsHandler(InputHandler):
    def __init__(self, allowed_player: Player):
        """
        @param allowed_player: The only player that this will react to
        """
        self.allowed_player = allowed_player

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):

        if player != self.allowed_player or player_input.get_command().lower() != "setting" \
                or type(player.player_output) is not StreamOutput:
            return None

        output: StreamOutput = player.player_output

        def handle_function(already_handled: List[InputHandleType]) -> InputHandleType:
            if len(player_input.get_arg(1)) != 0:
                if player_input.get_arg(0)[0].lower() == "speed":
                    speed = player_input.get_arg(1)[0].lower()
                    if speed == "fast":
                        output.wait_multiplier = 0.4
                        player.send_message("Set speed to fast.")
                        return InputHandleType.HANDLED_AND_DONE
                    elif speed == "normal":
                        output.wait_multiplier = 1
                        player.send_message("Set speed to normal")
                        return InputHandleType.HANDLED_AND_DONE
                    else:
                        pass  # flow down to send help message

            player.send_message(Message("Help for setting command: \n"
                                        "\tspeed: setting speed <fast:normal>", MessageType.IMMEDIATE))
            return InputHandleType.HANDLED_AND_DONE

        return InputHandle(0, handle_function, self)
