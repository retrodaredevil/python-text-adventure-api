import warnings
from abc import abstractmethod
from typing import List, Optional, TypeVar, Type

from textadventure.entity import EntityAction, Entity
from textadventure.handler import Handler
from textadventure.input.inputhandling import InputHandler
from textadventure.input.inputhandling import InputObject
from textadventure.item.holder import Holder
from textadventure.item.item import Item, FiveSensesHandler
from textadventure.message import Message, MessageType
from textadventure.player import Player
from textadventure.utils import Point, MessageConstant, are_mostly_equal, CanDo

T = TypeVar('T')


class Location(Holder, InputHandler, FiveSensesHandler):
    NO_YELL_RESPONSE: MessageConstant = "There was no response."

    """
    The Location is an abstract base class used for all Locations. Many of the methods aren't meant to be called \
    randomly outside of a specific set of classes that handle those methods. Most of the methods in here should never\
    be called randomly unless it's something like get_players or is_lit_up.
    
    Also note one of the primary features of this class is that it is also an input handler but you have to call \
        _should_take_input to make sure that the player is in this location.
        
    Note that with the inherited methods from FiveSensesHandler, usually, player.location will be self, but you\
        should program each method carefully and prepare if the player smelling, looking from another location. \
        Note that you shouldn't throw assert errors because that would defeat the whole point.  
    Attributes:
        command_handlers: Keeps a list of command_handlers. After __init__ is called, Handler should call these \
                          when location is getting its on_input called
    """

    def __init__(self, name, description, point: Point):
        from textadventure.commands.command import CommandHandler
        super().__init__()
        self.name = name
        self.description = description
        self.point: Point = point  # noinspection PyTypeChecker

        self.command_handlers: List[CommandHandler] = []
        self.__add_command_handlers()

    def __str__(self):
        return self.name

    def __add_command_handlers(self) -> None:
        """
        Should only add to command_handlers using append or extend
        When I first made all of these CommandHandlers Location specific I thought I was giving more control to each \
            location object. But I think if I ever decide to make these act on whatever location the player \
            is currently at, it would have the exact same effect. I'm leaving like this for now though.
        :return: None
        """
        from textadventure.commands.commands import LookCommandHandler, FeelCommandHandler, SmellCommandHandler, \
            TasteCommandHandler, ListenCommandHandler
        self.command_handlers.extend([LookCommandHandler(self), FeelCommandHandler(self), SmellCommandHandler(self),
                                      TasteCommandHandler(self), ListenCommandHandler(self)])

    def is_reference(self, reference: str) -> bool:
        """
        Returns if the given string is close enough to this locations name
        :param reference: The string that is close to the location name
        :return: True if the reference string is close enough to reference this location
        """
        return are_mostly_equal(self.name, reference)

    def on_take(self, handler: Handler, item: Item) -> None:
        """
        By default, doesn't do anything. Is called after the weapon's change_holder is called and should not be called\
            inside the weapon's change_holder function
        You can use the weapon's holder to see it's new holder and since it was taken, it's previous holder is this loc
        :param handler: The handler object
        :param item: The weapon that was taken
        :return: None
        """
        pass

    def on_place(self, handler: Handler, item: Item, player: Player) -> None:
        """
        Just like on_take , it's called after weapon's change_holder and is not called by that method
        The weapon's holder is already this location. The player is what placed it

        Note instead of overriding (or listening) for this method, you can override the @see can_hold method if needed
        :param handler: The handler object
        :param item: The weapon placed
        :param player: The player who placed/dropped the weapon
        :return: None
        """
        pass

    def on_yell(self, handler: Handler, player: Player, player_input: InputObject, is_there_response=False) -> None:
        """
        There is a default player implementation for this
        is_there_response is only meant to be changed by inheriting classes (It shouldn't be changed by YellCommandHa..)
        :param handler: The handler object
        :param player: The player
        :param player_input: The player input object
        :param is_there_response: By default,False. If set to true, the default implementation won't
                                        say no one responded
        :return: None
        """
        first_arg = player_input.get_arg(0, False)
        player.send_message(Message("You (Yelling): {}".format(" ".join(first_arg)), MessageType.IMMEDIATE))
        player.send_message(Message("....", message_type=MessageType.TYPE_SLOW))
        if not is_there_response:
            player.send_message(self.__class__.NO_YELL_RESPONSE)

    def on_item_use(self, handler: Handler, player: Player, item: Item) -> None:
        """
        Should be called by the UseCommandHandler.
        If overridden, it's recommended that you call the super method (this method)
        :param handler: The handler object
        :param player: The player object
        :param item: The weapon that is being 'used'
        :return: None because the this Location should choose how it wants to handle the using of this weapon
        """
        player.send_message("You can't use that weapon here.")
        # ONEDAY here, we will eventually handle simple things that all locations should be able to handle

    def _send_welcome(self, player: Player):
        """
        The default method that should be called by a subclass of Location.
        Because this begins with an _, it is not called except by subclasses of Location
        :param player: The player to send the message to
        :return: None
        """
        player.send_message(self.name + ": " + self.description)

    def send_locate_message(self, player: Player):
        player.send_message(Message("You are at {}, which is '{}'", named_variables=[self.point, self]))

    def update(self, handler: Handler):
        """
        By default, doesn't do anything unless overridden
        This method should be called on the infinite loop by handler
        :param handler: the handler object
        """
        pass

    @abstractmethod
    def on_enter(self, player: Player, previous_location: Optional['Location'], handler: Handler):
        """
        Should be called when the player's location is changed (this method doesn't set the players location)
        If for whatever reason, this method may change the player's location back to the previous (update if becomes t)
        When overriding, make sure that even if the player doesn't leave and this method gets called twice for whatever\
            reason, it doesn't do something like give them a second weapon or make them face an enemy they already faced
        :param handler:
        :param player: The player
        :param previous_location: the previous location or None if there is none or it couldn't be found
        :type previous_location: Location
        :rtype: None
        """
        pass

    @abstractmethod
    def go_to_other_location(self, handler: Handler, new_location, direction: Point, player: Player) -> CanDo:
        """
        Called when a player tried to go to another location using the go command. Different implementation for each \
        loc Note that when overriding this method, try not use use the type reference to other locations as the \
        compiler won't like you
        This method will call on_enter, change the player's location etc if it is a success

        :param handler:
        :param player: The player that is trying to go to the new_location
        :param new_location: The new location that the player is trying to go to. If passed is None, respond to \
                a direction
        :param direction: The direction the player will move/ add to this location to get new_location's point
        :return: A CanDo tuple. If [0] is False, there was no output given to the player and the [1] \
                 represents the error message that still needs to be sent to the player. If [0] is True, then [1] \
                 tells why it is True (This should not be sent to the player)
        """
        pass

    def get_players(self, handler: Handler) -> List[Player]:
        return self.get_entities(handler, Player)

    def get_entities(self, handler: Handler, entity_type: Type[T] = Entity) -> List[T]:
        """
        Gets the list of entities in this location, including players
        :param handler: the handler object
        :param entity_type: The type of the entity you are looking for. Defaults to Entity (gets all types of entities)
        :return: The list of entities in this location
        """
        r = []
        for entity in handler.entities:
            if entity.location == self and isinstance(entity, entity_type):
                r.append(entity)

        return r

    def _should_take_input(self, handler: Handler, player: Player, player_input: InputObject):
        """
        A method that is called by a subclass of Location usually when handling input.
        The default implementation (That probably shouldn't be changed) checks to see if the player's location is self
        In the default implementation, handler and player_input are not used

        When handling input in an implementation of Location, this should almost always be called first to make sure\
            the player is at this location.
        """
        return player.location == self

    def get_referenced_entity(self, handler: Handler, reference: str):

        for entity in self.get_entities(handler):
            if entity.is_reference(reference):
                return entity

        return None

    def is_lit_up(self):
        """
        Tells if the location is lit up. Note that the locations's state affects this and not the player's state
        Note that I am not sure about the way we will eventually handle light, so think of this as deprecated
        :return: True if the location is lit up
        """
        return True


class GoAction(EntityAction):
    def __init__(self, entity: Entity, previous_location: Location, new_location: Location,
                 leave_message: MessageConstant, send_on_can_not: bool = False):
        """
        :param send_on_can_not: The value that is passed to the EntityAction init and now, instead of True, by default\
                            is False
        """
        super().__init__(entity, send_on_can_not=send_on_can_not)
        self.previous_location = previous_location
        self.new_location = new_location
        self.leave_message = leave_message

        if not isinstance(entity, Player):
            warnings.warn("Are you sure you should be sending this for an entity?")

    def _do_action(self, handler: Handler):
        self.entity.send_message(self.leave_message)

        self.entity.location = self.new_location

        if isinstance(self.entity, Player):
            self.entity.location.on_enter(self.entity, self.previous_location, handler)
        return self.can_do
