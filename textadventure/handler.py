import sys
from typing import List, Optional, TypeVar, Type, TYPE_CHECKING, Any, Union

from textadventure.action import Action
from textadventure.entity import Entity, Identifiable, Living
from textadventure.input.inputhandling import CommandInput, InputHandleType, InputHandler
from textadventure.manager import Manager
from textadventure.player import Player
from textadventure.saving.savables import PlayerSavable
from textadventure.saving.savable import Savable, HasSavable, SaveLoadException
from textadventure.saving.saving import SavePath, save_data, load_data
from textadventure.sending.commandsender import CommandSender
from textadventure.sending.message import Message, MessageType
from textadventure.utils import Point, get_type_from_list, TypeCollection, CanDo
from textprint.colors import Color

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
                 savable: Optional['HandlerSavable'], player_handler: Optional['PlayerHandler'] = None):
        """
        Creates the Handler object with parameters where some are able to change

        :param identifiables: The starting List of Identifiables. Normally, this list is very small or empty
                since the Handler object needs to be constructed to initialize some Identifiables.
        :param locations: List of all the locations in the game that normally should almost never change
        :param input_handlers: The list of starting InputHandlers where most of the elements shouldn't be removed.
        :param managers: The list of starting Managers
        :param save_path: The path where the game will be saved
        :param savable: The savable that handles the saving of the Handler object
        :param player_handler: The PlayerHandler object. By default, it is None which will create a new one
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
        self._savables = savable.savables if savable is not None else {}
        """
        A Dictionary of savables where the key is something that is usually a tuple with the first value
        being the name of the class that created it and the second value being a number or id to make sure that
        that class can create multiple of something. 
        
        The value is a Tuple where [0] is the savable, and [1] is the source that is used when saving it
        
        Note this does not include PlayerSavables. PlayerSavables are handled separately
        
        If this is something like a PlayerSavable, you should use their
        uuid because you aren't going to be creating a Player named Bob at one point in the code like you might
        create an entity named 'White Belt Ninja' once in the code
        """

        self.player_handler = player_handler if player_handler is not None else PlayerHandler(None, self)
        self.player_handler.handler = self

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

        # above for loop may append to self.identifiables so this loop is second
        # this was a terrible idea and broke some stuff
        # for ident in self.identifiables:
        #     if isinstance(ident, HasSavable):
        #         if ident.savable is not None:
        #             ident.savable.on_load(ident, self)
        # assert next(iter(self.get_players()))[PlayerFriend] is not None this is just debug that helped find problem

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

    def save(self, sender: Optional[CommandSender] = None) -> CanDo:
        """
        Saves data for the running game. If you want to change the save path, set save_path before you call this method
        as this method uses self.save_path to determine where to save the data
        :return: A CanDo representing whether or not the handler data saved successfully. The return value at [1]
                 should always be displayed to the user.
        """
        is_valid = self.save_path.is_valid()
        if not is_valid[0]:
            return is_valid
        handler_result = self._save_handler()
        if not handler_result[0]:
            return handler_result

        unsaved_string = ""
        unsaved_amount = 0
        for player in self.get_players():
            # sender.send_message(Message("Saving: {}", named_variables=[player]))
            player_result = self.player_handler.save_player(player)
            if not player_result[0]:
                sender.send_message(Message(str(player.uuid) + " - " + player_result[1],
                                            message_type=MessageType.IMMEDIATE))
                unsaved_amount += 1

        if unsaved_amount:
            unsaved_string = " {} players were unable to be saved.".format(unsaved_amount)

        return True, "You successfully saved data to {}.".format(self.save_path) + unsaved_string

    def _save_handler(self) -> CanDo:
        path = self.save_path.get_handler_path()
        self.savable.before_save(self, self)
        return save_data(self.savable, path)

    # region all getters
    def get_savable(self, key) -> Union[Savable, Any]:
        """
        :return: A Tuple where [0] is the Savable and [1] is the source that should be used when saving. When loading,
                 this will always be None because it is not actually saved.
        """
        return self._savables.get(key, None)

    def set_savable(self, key, savable: Savable, source: Any):
        """
        Sets the savable so get_savable(key) returns value.

        :param key: The key. Usually A UUID or a Tuple[str, int]. It should never contain something like a type or
                an instance of an object because we want it to be something if if saved, won't conflict later while
                loading
        :param savable: The savable
        :param source: The source when saving the savable
        :return: None
        """
        self._savables[key] = (savable, source)

    def get_savables(self):
        """Should only be used in handler.py and nowhere else."""
        return self._savables

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
        self.savables = None  # type Dict[Any, Tuple[Savable, NoneType]]

    def before_save(self, source: Any, handler: 'Handler'):
        assert source is handler
        self.savables = {}
        for key, value in handler.get_savables().items():
            savable, source = value
            savable.before_save(source, handler)
            self.savables[key] = savable, None
            # print("saving: '{}' with '{}' as source".format(savable, source))

    def on_load(self, source: Any, handler: 'Handler'):
        assert source is handler
        assert source.get_savables() == self.savables, "The handler object is expected to apply variables."
        # this does nothing because we expect that Handler's init used this instance to already initialize variables.


class PlayerHandler:
    """
    A class where one instance of this class belongs to the Handler instance and this classes sole purpose is to
    separate methods used for saving players, loading players, and validating player names etc.

    This class also assumes that any players that already have names that aren't None, are valid and are not duplicates.
    Unless some other code altered the names or something, this should not be a problem if you just let this class
    handle it
    """
    _VALID_RANGES = [range(48, 57 + 1), range(65, 91 + 1), range(95, 95 + 1), range(97, 122 + 1)]

    def __init__(self, save_path: Optional[SavePath], handler: Optional[Handler] = None):
        """
        :param save_path: The save path. Note if handler is not None, this will not be used. If handler it not None,
                          that should be the only instance where this can be None
        :param handler: The handler or None if it has not been initialized yet.
        """
        if save_path is None and handler is None:
            raise ValueError("Each provided argument was None. One of them has to not be None.")
        self._save_path = save_path
        self.handler = handler

        self.player_savables = []  # type List[PlayerSavable]

    def get_save_path(self):
        return self.handler.save_path if self.handler is not None else self._save_path

    def load_player_savables(self) -> CanDo:
        """
        Loads all saved player data from the player directory
        :return: A CanDo where [0] is True if it loaded any amount of player savables correctly. [1] is the result and
                 should be displayed no matter what [0] is. Note that [1] may have multiple lines. The first line
                 says "Loaded {} players successfully. {} others unsuccessfully" while other lines are errors
        """
        folder = self.get_save_path().get_player_folder()
        if not folder.exists():
            return False, "The player directory does not exist"
        if not folder.is_dir():
            return False, "The player directory is not a directory."

        errors = []
        good_amount = 0
        for item in folder.iterdir():
            if item.is_file():
                data = load_data(item)
                if isinstance(data, PlayerSavable):  # probably a PlayerSavable, but what do we care?
                    self.player_savables.append(data)
                    good_amount += 1
                elif isinstance(data, str):  # this is the error message
                    errors.append("File: {} - ".format(item.name) + data)
                else:
                    errors.append("File: {} - Loaded unknown data of type: {}".format(item.name, type(data)))

        error_string = ""
        if len(errors) > 0:
            error_string = "{} others unsuccessfully:\n".format(len(errors))
            error_string += "\n".join(errors)
        return good_amount > 0, "Loaded {} players successfully. ".format(good_amount) + error_string

    def get_player_savable(self, name: str) -> Optional[PlayerSavable]:
        """
        Finds the player with the name of name. Note you must call load_player_savables for this to get updated data
        but you shouldn't have to worry about it because every time a player leaves, they should save the game

        This function compares the names of the saved players and ignores the case
        :param name: The name of the player's savable to get
        :return: The savable with that belongs to the player with the name of name or None if it was not found
        """
        for save in self.player_savables:
            if save.name.lower() == name.lower():
                return save
        return None

    def is_name_taken(self, name: str) -> bool:
        if self.handler is not None:
            for player in self.handler.get_players():
                if player.name is not None and player.name.lower() == name.lower():
                    return True
        return self.get_player_savable(name) is not None

    def is_name_valid(self, name):
        if name is None:
            return False

        return all(any(ord(c) in r for r in self.__class__._VALID_RANGES) for c in name)

    def save_player(self, player: Player) -> CanDo:
        assert self.handler is not None
        path = self.get_save_path().get_player_path(player)
        try:
            player.savable.before_save(player, self.handler)
        except SaveLoadException as e:
            return False, e.args[0]
        return save_data(player.savable, path)
