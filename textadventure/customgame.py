from abc import ABC, abstractmethod
from typing import List

from textadventure.actions import EntityActionToEntityManager
from textadventure.battling.commands import AttackCommandHandler
from textadventure.battling.managing import DamageActionManager, BattleManager, HostileEntityManager
from textadventure.commands.commands import GoCommandHandler, TakeCommandHandler, PlaceCommandHandler, \
    YellCommandHandler, UseCommandHandler, NameCommandHandler, InventoryCommandHandler, LocateCommandHandler, \
    HelpCommandHandler, DirectionInputHandler
from textadventure.handler import Handler
from textadventure.input.inputhandling import InputHandler
from textadventure.location import Location
from textadventure.manager import Manager
from textadventure.player import Player
from textadventure.saving.saving import SaveCommandHandler, LoadCommandHandler


class CustomGame(ABC):
    """
    A class that is designed to hold methods that return objects to be added to the handler to make each game unique

    This class does not contain methods that are called constantly and does not contain data that is constantly needed\
    this is used for holding methods that are for initialization of the game
    """

    def __init__(self, name):
        """
        Creates a CustomGame.

        :param name: The name of the game
        """
        self.name = name

    @abstractmethod
    def create_locations(self, handler: Handler) -> List[Location]:
        """
        An abstract method that should return all of the locations that will be used in the game. Most of the time,\
        you shouldn't need to use the handler for anything unless a location wants to add an entity to \
        handler.entities.

        :param handler: The Handler object
        :return: A list of locations
        """
        pass

    @abstractmethod
    def new_player(self, player: Player):
        """
        An abstract method that is called whenever a new player joins the game. It should be used to give the player\
        necessary objects like a Savable, and other things that can be used to keep track of progress, or have \
        custom things

        Remember, this method is only called when there is a new player

        :param player: The new player that joined
        """
        pass

    @abstractmethod
    def create_custom_input_handlers(self) -> List[InputHandler]:
        """
        Returns custom input handlers.

        :return: A list of InputHandlers
        """
        pass

    def create_input_handlers(self) -> List[InputHandler]:
        return [GoCommandHandler(), TakeCommandHandler(), PlaceCommandHandler(), YellCommandHandler(),
                UseCommandHandler(), SaveCommandHandler(), LoadCommandHandler(), NameCommandHandler(),
                InventoryCommandHandler(), LocateCommandHandler(), HelpCommandHandler(), AttackCommandHandler(),
                DirectionInputHandler()
                ]

    @abstractmethod
    def create_custom_managers(self, handler: Handler) -> List[Manager]:
        """
        Returns custom Managers

        :param handler: The handler object
        :return: A list of Managers
        """
        pass

    def create_managers(self, handler: Handler) -> List[Manager]:
        return [HostileEntityManager(), EntityActionToEntityManager(), BattleManager(), DamageActionManager()]

    @abstractmethod
    def add_other(self, handler: Handler) -> None:
        """
        Called after adding InputHandlers, and Managers. It should be used to add things to the handler like Livings\
        or just other things in general that wouldn't make sense to put in the create... methods

        :param handler: The handler object that implementations of this method are free to alter or add to
        :return: None
        """
        pass
