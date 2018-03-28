from typing import List, Optional, TypeVar, Type, TYPE_CHECKING, Any

from textadventure.action import Action
from textadventure.entity import Entity, Identifiable, Living
from textadventure.input.inputhandling import CommandInput, InputHandleType, InputHandler
from textadventure.manager import Manager
from textadventure.player import Player
from textadventure.saving.savable import Savable, HasSavable
from textadventure.saving.saving import SavePath, save_data
from textadventure.sending.commandsender import CommandSender
from textadventure.utils import Point, get_type_from_list, TypeCollection, CanDo

if TYPE_CHECKING:
    from textadventure.location import Location
# to future self, most of these imports would be in this if statement, but I assure you none of them can be.
# if that changes, move as many as you can to the if statement


T = TypeVar("T")


def has_only(the_list: List[T], only_list: List[T]):
    """
    Checks to make sure that all the items that are in the_list are in only_list

    :param the_list: The list to check
    :param only_list: The list of acceptable objects to make sure that every element in the list is one of these objects
    :return: True if all the items in the list are equal to only, Also True if there are no items in list.
    """
    for ele in the_list:
        if ele not in only_list:
            return False
    return True


class Handler(HasSavable):
    """
    Although initializing data in this class requires other classes, this class holds all necessary data and functions
    to keep the game running without help from other object.
    """

    def __init__(self, identifiables: List[Identifiable], locations: List['Location'],
                 input_handlers: List[InputHandler], managers: List[Manager], save_path: SavePath,
                 savable: Optional['HandlerSavable']):
        """
        Creates the Handler object with parameters where some are able to change

        :param identifiables: The starting List of Identifiables. Normally, this list is very small or empty
                since the Handler object needs to be constructed to initialize some Identifiables. Don't be afraid to
                pass an empty list or a list with one Player.
        :param locations: List of all the locations in the game that normally should almost never change
        :param input_handlers: The list of starting InputHandlers where most of the elements shouldn't be removed.
        :param managers: The list of starting Managers
        :param save_path: The path where the game will be saved
        :param savable: The savable that handles the saving of the Handler object
        """
        super().__init__(savable)
        self.identifiables = identifiables
        """Contains Players, Entities and other types of Identifiables. Note that when a player is added to this list,
        it should and will be saved separately. 
        
        Other elements like Entities that aren't Players will only be saved
        if you have called set_savable and passed a Savable that will handle saving and loading for the Entity or
        Identifiable. (Only players are saved automatically)"""
        self.locations = locations
        self.input_handlers = input_handlers
        """A list of InputHandlers that do not include Locations"""
        self.managers = managers
        self.save_path = save_path

        # Variables not from the constructor
        """Can be used by the save and load command to easily save and load things"""
        if savable is None:
            self._savables = {}
            """
            A Dictionary of savables where the key is something that is usually a tuple with the first value
            being the name of the class that created it and the second value being a number or id to make sure that
            that class can create multiple of something. 
            
            Note this does not include PlayerSavables. PlayerSavables are handled separately
            
            If this is something like a PlayerSavable, you should use their
            uuid because you aren't going to be creating a Player named Bob at one point in the code like you might
            create an entity named 'White Belt Ninja' once in the code
            """
        else:
            self._savables = savable.savables

        self.living_things = []
        """A list of livings that normally should never change. It's used to keep track of Living
        objects which make them easy to retrieve without using a static variable in the class of the living"""
        self.should_end = False
        """
        When True, what ever is calling the update method should stop their infinite loop, and terminate the program.
        """

    def _create_savable(self):
        return HandlerSavable()

    def start(self):
        """
        Should be called before the first time update is called. (Does not do this automatically - do this manually)
        """
        for location in self.locations:  # TODO should we initialize stuff in here?
            for initializer in location.initializers:
                initializer.do_init(self)

    def update(self):
        """
        Should be called repeatedly after calling start
        """
        if self.should_end:
            self.broadcast("The program should have already ended.")
            return

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
        if sender.output.on_input(sender, input_object):
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

    def save(self) -> CanDo:
        """
        Saves data for the running game. If you want to change the save path, set SAVE_PATH before you call this method
        as this method uses self.SAVE_PATH to determine where to save the data
        :return: A CanDo representing whether or not the data saved successfully. The return value at [1] should always
                 be displayed to the user.
        """
        is_valid = self.save_path.is_valid()
        if not is_valid[0]:
            return is_valid
        handler_result = self._save_handler()
        if not handler_result[0]:
            return handler_result

        for player in self.get_players():
            player_result = self._save_player(player)
            if not player_result[0]:
                return player_result

        return True, "You successfully saved data to {}".format(self.save_path)

    def _save_handler(self) -> CanDo:
        path = self.save_path.get_handler_path()
        self.savable.before_save(self, self)
        return save_data(self.savable, path)

    def _save_player(self, player: Player) -> CanDo:
        path = self.save_path.get_player_path(player)
        player.savable.before_save(player, self)
        return save_data(player.savable, path)

    # region all getters
    # region savable and savables getters/setters
    def get_savable(self, key):
        return self._savables.get(key, None)

    def set_savable(self, key, value: Savable):
        """
        Sets the savable so get_savable(key) returns value.

        :param key: The key. Usually A UUID or a Tuple[str, int]. It should never contain something like a type or
                an instance of an object because we want it to be something if if saved, won't conflict later while
                loading
        :param value:
        :return: None
        """
        self._savables[key] = value
    # endregion

    def get_input_handlers(self) -> List[InputHandler]:
        r = []
        for location in self.locations:
            r.append(location)
            r.extend(location.command_handlers)
        for inp in self.input_handlers:
            r.append(inp)

        return r

    def get_location(self, location_type: type):
        """
        :param location_type: The type of the location you are trying to get
        :return:
        """
        for location in self.locations:
            # print("location's type: " + str(type(location)))
            # print("location_type: " + str(location_type))
            if type(location) is location_type:
                return location
        return None

    # region identifiable getters
    def get_players(self) -> TypeCollection[Player]:
        # r = []
        # for entity in self.identifiables:
        #     if isinstance(entity, Player):
        #         r.append(entity)
        # return r
        # return get_type_from_list(self.identifiables, Player, None)
        return TypeCollection(self.identifiables, [Player])

    def get_entities(self) -> TypeCollection[Entity]:
        # return get_type_from_list(self.identifiables, Entity, None)
        return TypeCollection(self.identifiables, [Entity])

    def get_command_senders(self) -> TypeCollection[CommandSender]:
        # return get_type_from_list(self.identifiables, CommandSender, None)
        return TypeCollection(self.identifiables, [CommandSender])
    # endregion

    def get_managers(self, manager_types: Type[Manager], expected_amount: Optional[int] = None) -> List[Manager]:
        """Quick note, manager_types can be a single type or a list of types. See docs for get_type_from_list"""
        return get_type_from_list(self.managers, manager_types, expected_amount)

    def get_livings(self, living_types: Type[Living], expected_amount: Optional[int] = None) -> List[Living]:
        """Quick note, living_types can be a single type or a list of types. See docs for get_type_from_list"""
        return get_type_from_list(self.living_things, living_types, expected_amount)

    def get_point_location(self, point: Point):
        for location in self.locations:
            if location.point == point:
                return location
        return None
    # endregion end all getters

    def broadcast(self, message):
        for player in self.get_players():
            player.send_message(message)

    def debug(self, message):
        self.broadcast(message)


class HandlerSavable(Savable):
    def __init__(self):
        super().__init__()
        self.savables = {}  # type Dict[Any, Savable]

    def before_save(self, source: Any, handler: 'Handler'):
        assert source is handler
        self.savables = dict(source.get_savables())  # store a clone of Handler's savable dict

    def on_load(self, source: Any, handler: 'Handler'):
        assert source is handler
        assert source.get_savables() == self.savables, "The handler object is expected to apply variables."
        # this does nothing because we expect that Handler's init used this instance to already initialize variables.
