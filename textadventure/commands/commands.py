from abc import abstractmethod
from typing import List, Optional

from textadventure.commands.command import LocationCommandHandler, SimpleCommandHandler
from textadventure.entity import Entity
from textadventure.handler import Handler
from textadventure.input.inputhandling import CommandInput, InputHandleType, InputHandler, InputHandle, \
    PlayerInputHandler
from textadventure.item.holder import Holder
from textadventure.item.item import FiveSensesHandler, Item
from textadventure.location import Location
from textadventure.player import Player
from textadventure.sending.commandsender import CommandSender
from textadventure.sending.message import Message, MessageType
from textadventure.utils import Point, NORTH, EAST, SOUTH, WEST, UP, DOWN, ZERO, CanDo

"""This file holds some nice commands and util methods that help out with it. Most of the commands are essential."""


def get_reference(player: Player, string_args: str) -> Optional[Item]:
    """
    Senses command handler has a good code snippet that shows how you should use this method
    Note: Remember, this can return None.

    :param player: the player
    :param string_args: The arguments that the player entered
    :return: The weapon
    """
    for item in player.location.items:
        if item.is_reference(string_args):
            return item
    for item in player.items:
        if item.is_reference(string_args):
            return item
    return None


def get_point(handler: Handler, player: Player, string_args: str) -> Optional[Point]:
    """
    Gets the location using the player, and it's string_args

    :param handler: The Handler object
    :param player: The player. Needed for location reference to get location N,E,S,W
    :param string_args: The string arguments
    :return: The point object that represents the point of the new location
    """
    for location in handler.locations:  # we do this first in case there's a location called North <something>
        if location.is_reference(string_args):
            return location.point
    # now we'll check if it's a direction
    string_args = string_args.lower()
    # add = None  we don't need declaration because it does it in if clauses that are needed
    if "nor" in string_args:
        add = NORTH
    elif "eas" in string_args:  # or "ast" in string_args can't cuz taste <:  # can't put est here because of west
        add = EAST
    elif "sou" in string_args:
        add = SOUTH
    elif "wes" in string_args:
        add = WEST
    elif "up" in string_args:
        add = UP
    elif "dow" in string_args:
        add = DOWN
    elif "her" in string_args:
        add = ZERO
    else:  # note that this is the only clause that returns.
        return None
    if add is None:
        raise Exception("Should not have happened")
    return player.location.point + add


class HelpCommandHandler(SimpleCommandHandler):
    def __init__(self):
        super().__init__(["help"], "The help for this command isn't very helpful now it it?")

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput) -> InputHandleType:
        sender.send_message(Message("Get help for commands: '<command> help'", message_type=MessageType.IMMEDIATE))
        sender.send_message(
            Message("Useful commands: 'go', 'look', 'listen', 'feel', 'taste', 'smell', 'locate', 'items'"))
        return InputHandleType.HANDLED


"""
The SensesCommandHandler and all the 5 command handler that are subclasses of that are LocationCommandHandlers because\
we want to give the Location as much control over these as possible (that's why they are part of the location's\
field, command_handlers. They should be specific to each location to give it control over these)
"""


class SensesCommandHandler(LocationCommandHandler):
    def __init__(self, command_names: List[str], description: str, location: Location):
        super().__init__(command_names, description, location)

    @abstractmethod
    def sense(self, sense_handler: FiveSensesHandler, handler: Handler, player: Player):
        """
        Should be overridden and should only call the method from sense_handler. (Should not try to call \
                can_sense) (It should call sense_handler.<sense_name>(<needed parameters>) no matter what)

        :param sense_handler: The object that the player is trying to use this sense on. Could be a location, item, etc
        :param handler: The handler object
        :param player: The player that is trying to use this sense
        """
        pass

    @abstractmethod
    def can_sense(self, item: Item, player: Player) -> CanDo:
        """
        Tells you whether or not you are able to perform the sense that this class represents on the item

        :param item: The item that you are trying to perform the sense action on
        :param player: The player that is trying sense the item
        :return: A CanDo representing if the player is able to sense the current item. [1] represents a message that\
                should be sent to the player if [0] is False (Sent if the player isn't able to perform the action)
        """
        pass

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput) -> InputHandleType:
        if not isinstance(sender, Player):
            return InputHandleType.NOT_HANDLED

        first_arg = command_input.get_arg(0)
        if len(first_arg) != 0:  # thing stuff
            # here to
            referenced_item = get_reference(sender, " ".join(first_arg))
            if referenced_item is None:
                sender.send_message(Item.CANNOT_SEE[1])
                return InputHandleType.HANDLED
            can_ref = referenced_item.can_reference(sender)
            if can_ref[0] is False:
                sender.send_message(can_ref[1])
            else:  # here is how you should use get_reference
                can_do_sense = self.can_sense(referenced_item, sender)
                if can_do_sense[0]:
                    self.sense(referenced_item, handler, sender)
                else:
                    sender.send_message(can_do_sense[1])
        else:  # location stuff
            self.sense(sender.location, handler, sender)
        return InputHandleType.HANDLED


class LookCommandHandler(SensesCommandHandler):
    command_names = ["look", "see", "lok", "find", "se", "ook"]  # yeah I know, magic strings deal with it
    description = """Allows you to see your surroundings. Aliases: look, see, find\nUsage: look [weapon] """

    def __init__(self, location: Location):
        super().__init__(self.__class__.command_names, self.__class__.description, location)

    def sense(self, sense_handler: FiveSensesHandler, handler: Handler, player: Player):
        sense_handler.see(handler, player)

    def can_sense(self, item: Item, player: Player) -> CanDo:
        return item.can_see(player)


class ListenCommandHandler(SensesCommandHandler):
    command_names = ["listen", "hear", "escucha", "liste", "isten", "hea", "listne"]
    description = """Allows you to listen to your surroundings. Aliases: listen, hear\nUsage: feel [weapon]"""

    def __init__(self, location: Location):
        super().__init__(self.__class__.command_names, self.__class__.description, location)

    def sense(self, sense_handler: FiveSensesHandler, handler: Handler, player: Player):
        sense_handler.listen(handler, player)

    def can_sense(self, item: Item, player: Player) -> CanDo:
        return item.can_listen(player)


class FeelCommandHandler(SensesCommandHandler):
    command_names = ["feel", "touch", "eel", "fee", "tou", "tuch", "toch"]
    description = """Allows you to feel your surroundings. Aliases: look, touch\nUsage: feel [weapon]"""

    def __init__(self, location: Location):
        super().__init__(self.__class__.command_names, self.__class__.description, location)

    def sense(self, sense_handler: FiveSensesHandler, handler: Handler, player: Player):
        sense_handler.feel(handler, player)

    def can_sense(self, item: Item, player: Player):
        return item.can_feel(player)


class SmellCommandHandler(SensesCommandHandler):
    command_names = ["smell", "nose", "smel", "mell", "nos", "smeel", "smee", "mel"]
    description = """Allows you to smell your surroundings. Aliases: smell, nose\nUsage: feel [weapon]"""

    def __init__(self, location: Location):
        super().__init__(self.__class__.command_names, self.__class__.description, location)

    def sense(self, sense_handler: FiveSensesHandler, handler: Handler, player: Player):
        sense_handler.smell(handler, player)

    def can_sense(self, item: Item, player: Player):
        return item.can_smell(player)


class TasteCommandHandler(SensesCommandHandler):
    command_names = ["taste", "tongue", "aste", "tast"]
    description = """Allows you to taste. Aliases: taste, tongue\nUsage: feel [weapon]"""

    def __init__(self, location: Location):
        super().__init__(self.__class__.command_names, self.__class__.description, location)

    def sense(self, sense_handler: FiveSensesHandler, handler: Handler, player: Player):
        sense_handler.taste(handler, player)

    def can_sense(self, item: Item, player: Player):
        return item.can_taste(player)


class GoCommandHandler(SimpleCommandHandler):  # written on friday with a football ninjagame

    command_names = ["go", "move", "mov", "ove", "va", "voy", "walk", "step"]
    description = "Allows you to go to another location usually nearby. Aliases: go, move\n" \
                  "Usage: go <location or direction>"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput) -> InputHandleType:
        if not isinstance(sender, Player):
            return InputHandleType.UNSUPPORTED_SENDER

        player = sender
        first_arg = command_input.get_arg(0)
        if not first_arg:
            self.send_help(player)
            return InputHandleType.HANDLED
        rest = " ".join(first_arg)
        return self.__class__.player_go(handler, player, rest)

    @staticmethod
    def player_go(handler: Handler, player: Player, first_argument: str) -> InputHandleType:
        # note that first_argument doesn't have to be a single word
        point = get_point(handler, player, first_argument)
        if point is None:
            player.send_message("Cannot find location: \"" + first_argument + "\"")
            return InputHandleType.HANDLED
        new_location = handler.get_point_location(point)
        if new_location == player.location:
            player.send_message("You're already in that location!")
            return InputHandleType.HANDLED

        result = player.location.go_to_other_location(handler, new_location, point - player.location.point, player)
        if not result[0]:
            player.send_message(result[1])
        return InputHandleType.HANDLED


class DirectionInputHandler(PlayerInputHandler):
    """
    This is not a normal SimpleCommandHandler because it needs to react to many different commands it its priority
    is higher than that of a SimpleCommandHandler

    This class just checks to see if the player typed a single word and if that word matches a direction or location,
        treat the command just like the go command by called GoCommandHandler.player_go
    This InputHandler is called before normal command handles since this isn't actually a command handler
    """
    def __init__(self):
        super().__init__()

    def on_player_input(self, handler: Handler, player: Player, command_input: CommandInput):
        def handle_function(already_handled: List[InputHandleType]) -> InputHandleType:
            if not self._should_handle_input(already_handled):
                return InputHandleType.NOT_HANDLED
            return GoCommandHandler.player_go(handler, player, command_input.get_command())

        if not command_input.get_arg(0):  # make sure the length is always 1 (there should be no args cuz command)
            command_name = command_input.get_command()

            if get_point(handler, player, command_name) is not None:  # we'll let the GoCommandHandler do what it wants
                return InputHandle(InputHandle.PRIORITY_COMMAND_ALIAS, handle_function, self)
        return None


class TakeCommandHandler(SimpleCommandHandler):
    command_names = ["take", "grab", "tak", "steal", "pick", "pik", "pickup"]
    description = "Allows you to take something from a location or someone. Aliases: take, grab, pickup\n" \
                  "Usage: take <weapon name>"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        if not isinstance(sender, Player):
            return InputHandleType.UNSUPPORTED_SENDER
        player = sender
        first_arg = command_input.get_arg(0)
        if not first_arg:
            self.send_help(player)
            return InputHandleType.HANDLED
        item = get_reference(player, " ".join(first_arg))

        if item is None:
            player.send_message(Item.CANNOT_SEE[1])
            return InputHandleType.HANDLED
        can_ref = item.can_reference(player)
        if can_ref[0] is False:
            player.send_message(can_ref[1])
            return InputHandleType.HANDLED
        can_take = item.can_take(player)
        if can_take[0] is False:
            player.send_message(can_take[1])
            return InputHandleType.HANDLED

        # if we are here, the player is allowed to take this item

        if item in player.location.items:
            if item.change_holder(player.location, player):
                player.location.on_take(handler, item, player)
                player.send_message(Message("You took {}.", named_variables=[item]))
        else:
            player.send_message("You were unable to take the item because we couldn't find who had the item.\n"
                                "Obviously, this is kind of embarrassing so please tell someone what you did "
                                "so it can be fixed.")

        # previous_holder = item.holder
        # if item.change_holder(previous_holder, player) and isinstance(previous_holder, Location):
        #     previous_holder.on_take(handler, item)
        return InputHandleType.HANDLED


class PlaceCommandHandler(SimpleCommandHandler):
    command_names = ["place", "put", "plac", "drop"]
    description = "Allows you to place something in your current location. Aliases: place, put, drop\n" \
                  "Usage: place <weapon name>"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        if not isinstance(sender, Player):
            return InputHandleType.UNSUPPORTED_SENDER

        player = sender
        first_arg = command_input.get_arg(0)
        if not first_arg:
            self.send_help(player)
            return InputHandleType.HANDLED
        item = get_reference(player, " ".join(first_arg))

        if item is None:
            player.send_message(Item.CANNOT_SEE[1])
            return InputHandleType.HANDLED
        can_ref = item.can_reference(player)
        if can_ref[0] is False:
            player.send_message(can_ref[1])
            return InputHandleType.HANDLED
        can_put = item.can_put(player)
        if can_put[0] is False:
            player.send_message(can_put[1])
            return InputHandleType.HANDLED
        if item in player.items:
            if item.change_holder(player, player.location):
                player.location.on_place(handler, item, player)
                player.send_message(Message("You placed {}.", named_variables=[item]))
        else:
            player.send_message("Apparently, that item that you tried to place isn't in your inventory.\n"
                                "Please tell someone what you did so it can be fixed. (This message shouldn't appear)")
        return InputHandleType.HANDLED


class YellCommandHandler(SimpleCommandHandler):
    command_names = ["yell", "yel", "grita", "grito", "shout", "holler", "echo"]
    description = "Allows you to yell out something that someone or something may respond to. Use with caution.\n" \
                  "Aliases: yell\nUsage: yell <text to yell>"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def can_yell(self, player: Player) -> bool:
        """A simple abstraction that is used by _handle_command to check if the player is able to yell. However,\
            this only returns a bool so in the future, we could make it return a CanDo"""
        return True

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        if not isinstance(sender, Player):
            return InputHandleType.UNSUPPORTED_SENDER

        player = sender
        first_arg = command_input.get_arg(0, False)
        if not first_arg:
            self.send_help(player)
            return InputHandleType.HANDLED
        if self.can_yell(player):
            player.location.on_yell(handler, player, command_input)
        else:
            player.send_message("You can't yell right now.")
        return InputHandleType.HANDLED


class UseCommandHandler(SimpleCommandHandler):
    command_names = ["use"]
    description = "Allows you to use an weapon. Aliases: Use\n" \
                  "Usage: use <weapon name>"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        if not isinstance(sender, Player):
            return InputHandleType.UNSUPPORTED_SENDER

        player = sender
        first_arg = command_input.get_arg(0)
        if not first_arg:
            self.send_help(player)
            return InputHandleType.HANDLED
        item = get_reference(player, " ".join(first_arg))
        can_ref = Item.CANNOT_SEE  # by default, make it so they can't see the item
        if item is not None:
            can_ref = item.can_reference(player)  # check if they can reference/see the item
        if can_ref[0] is False:
            player.send_message(can_ref[1])
            return InputHandleType.HANDLED
        player.location.on_item_use(handler, player, item)
        return InputHandleType.HANDLED


class NameCommandHandler(SimpleCommandHandler):
    command_names = ["name"]
    description = "Allows you to tell what your own name is.\nUsage: name"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        sender.send_message(Message("Your name is {}.", named_variables=[sender]))
        return InputHandleType.HANDLED


class InventoryCommandHandler(SimpleCommandHandler):
    command_names = ["inv", "inventory", "inve", "invet", "invetory", "items"]
    description = "Allows you to see what's in your inventory"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        if not isinstance(sender, Holder):
            return InputHandleType.UNSUPPORTED_SENDER

        holder = sender
        amount = len(holder.items)
        if amount == 0:
            holder.send_message("You don't have anything in your inventory")
        elif amount == 1:
            holder.send_message(Message("You have {}.", named_variables=holder.items))
        else:
            names = []
            for i in range(0, amount):
                names.append("{}")

            holder.send_message(Message("You have these items: {}".format(", ".join(names)),
                                        named_variables=holder.items))

        return InputHandleType.HANDLED


class LocateCommandHandler(SimpleCommandHandler):
    command_names = ["locate", "location", "where", "loc"]
    description = "Allows you to tell where you are"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        if not isinstance(sender, Entity):
            return InputHandleType.UNSUPPORTED_SENDER

        sender.location.send_locate_message(sender)
        return InputHandleType.HANDLED


class SaveCommandHandler(SimpleCommandHandler):
    command_names = ["save"]
    description = "Allows you to save the game easily."

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, sender: CommandSender, command_input: CommandInput):
        result = handler.save()
        sender.send_message(result[1])
        return InputHandleType.HANDLED
