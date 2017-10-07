from abc import abstractmethod
from typing import List, Optional

from textadventure.holder import Holder
from textadventure.input import InputHandler
from textadventure.input import InputObject
from textadventure.item import Item, FiveSensesHandler
from textadventure.message import Message, MessageType
from textadventure.utils import Point, MessageConstant, are_mostly_equal, CanDo


class Location(Holder, InputHandler, FiveSensesHandler):
    from textadventure.player import Player
    from textadventure.handler import Handler

    NO_YELL_RESPONSE: MessageConstant = "There was no response."

    """
    The Location is an abstract base class used for all Locations. Many of the methods aren't meant to be called \
    randomly outside of a specific set of classes that handle those methods. Most of the methods in here should never\
    be called randomly unless it's something like get_players or is_lit_up. 
    Attributes:
        command_handlers: Keeps a list of command_handlers. After __init__ is called, Handler should call these \
                          when location is getting its on_input called
    """

    def __init__(self, name, description, point: Point):
        from textadventure.command import CommandHandler
        super().__init__()
        self.name = name
        self.description = description
        self.point: Point = point

        self.command_handlers: List[CommandHandler] = []
        self.__add_command_handlers()

        self.compare_names: List[str] = []
        """By default, it has only the name of the location. You can append to add more"""
        self.__add_compare_names()

    def __str__(self):
        return self.name

    def __add_command_handlers(self) -> None:
        """
        Should only add to command_handlers using append or extend
        When I first made all of these CommandHandlers Location specific I thought I was giving more control to each \
            location object. But I think if I ever decide to make these act on whatever location the player \
            is currently at, it would have the exact same effect. I'm leaving like this for now though.
        @return: None
        """
        from textadventure.commands import LookCommandHandler, FeelCommandHandler, SmellCommandHandler, \
            TasteCommandHandler, ListenCommandHandler
        self.command_handlers.extend([LookCommandHandler(self), FeelCommandHandler(self), SmellCommandHandler(self),
                                      TasteCommandHandler(self), ListenCommandHandler(self)])

    def __add_compare_names(self) -> None:
        """
        If overridden, remember to call super
        By default, adds the name to the list compare_names and name with unimportant words like "the" removed
        @return: None
        """
        self.compare_names.append(self.name)  # TODO actually implement this somewhere in the code

    def is_reference(self, reference: str) -> bool:
        """
        Returns if the given string is close enough to this locations name
        @param reference: The string that is close to the location name
        @return: True if the reference string is close enough to reference this location
        """
        return are_mostly_equal(self.name, reference)

    def on_take(self, handler: Handler, item: Item) -> None:
        """
        By default, doesn't do anything. Is called after the item's change_holder is called and should not be called\
            inside the item's change_holder function
        You can use the item's holder to see it's new holder and since it was taken, it's previous holder is this loc
        @param handler: The handler object
        @param item: The item that was taken
        @return: None
        """
        pass

    def on_place(self, handler: Handler, item: Item, player: Player) -> None:
        """
        Just like on_take , it's called after item's change_holder and is not called by that method
        The item's holder is already this location. The player is what placed it

        Note instead of overriding (or listening) for this method, you can override the @see can_hold method if needed
        @param handler: The handler object
        @param item: The item placed
        @param player: The player who placed/dropped the item
        @return: None
        """
        pass

    def on_yell(self, handler: Handler, player: Player, player_input: InputObject, is_there_response=False) -> None:
        """
        There is a default player implementation for this
        is_there_response is only meant to be changed by inheriting classes (It shouldn't be changed by YellCommandHa..)
        @param handler: The handler object
        @param player: The player
        @param player_input: The player input object
        @param is_there_response: By default,False. If set to true.The default implementation won't say no one responded
        @return: None
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
        @param handler: The handler object
        @param player: The player object
        @param item: The item that is being 'used'
        @return: None because the this Location should choose how it wants to handle the using of this item
        """
        player.send_message("You can't use that item here.")
        # ONEDAY here, we will eventually handle simple things that all locations should be able to handle

    def send_welcome(self, player: Player):
        player.send_message(self.name + ": " + self.description)

    def update(self, handler: Handler):
        """
        By default, doesn't do anything unless overridden
        This method should be called on the infinite loop by handler
        @param handler: the handler object
        """
        pass

    @abstractmethod
    def on_enter(self, player: Player, previous_location: Optional['Location'], handler: Handler):
        """
        Should be called when the player's location is changed (this method doesn't set the players location)
        If for whatever reason, this method may change the player's location back to the previous (update if becomes t)
        When overriding, make sure that even if the player doesn't leave and this method gets called twice for whatever\
            reason, it doesn't do something like give them a second item or make them face an enemy they already faced
        @param handler:
        @param player: The player
        @param previous_location: the previous location or None if there is none or it couldn't be found
        @type previous_location: Location
        @rtype: None
        """
        pass

    @abstractmethod
    def go_to_other_location(self, handler: Handler, new_location, direction: Point, player: Player) -> CanDo:
        """
        Called when a player tried to go to another location using the go command. Different implementation for each loc
        Note that when overriding this method, try not use use the type reference to other locations as the compiler\
        won't like you
        This method will call on_enter, change the player's location etc if it is a success
        @param handler:
        @param player: The player that is trying to go to the new_location
        @param new_location: The new location that the player is trying to go to. If passed is None, respond to a direction
        @param direction: The direction the player will move/ add to this location to get new_location's point
        @return: A CanDo tuple. If [0] is False, there was no output given to the player and the [1] \
                 represents the error message that still needs to be sent to the player. If [0] is True, then [1] \
                 tells why it is True (This should not be sent to the player)
        """
        pass

    def get_players(self, handler) -> List[Player]:
        r = []
        for player in handler.players:
            if player.location == self:
                r.append(player)
        return r

    def _should_take_input(self, handler: Handler, player: Player, player_input: InputObject):
        """
        A method that is called by a subclass of Location usually when handling input.
        The default implementation (That probably shouldn't be changed) checks to see if the player's location is self
        In the default implementation, handler and player_input are not used
        @param handler:
        @param player:
        @param player_input:
        @return:
        """
        return player.location == self

    def is_lit_up(self):
        """
        Tells if the location is lit up. Note that the locations's state affects this and not the player's state
        Note that I am not sure about the way we will eventually handle light, so think of this as deprecated
        @return: True if the location is lit up
        """
        return True
