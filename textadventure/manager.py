"""
If you are looking for the file that basically handles everything, look at handler.py
The Handler class does stuff with the stuff in this file
"""
from abc import ABC, abstractmethod

from textadventure.action import EntityAction


class Manager(ABC):

    @abstractmethod
    def update(self, handler):
        """
        Called each frame by handler
        @param handler: The handler object
        @type handler: Handler
        """
        pass

    @abstractmethod
    def can_entity_do_action(self, handler, action: EntityAction):
        """
        Called when an entity tries to do something that needs to be check to make sure they can do that
        @param handler: The Handler object
        @param action: The action that contains all the event information and has the necessary information/methods \
                        to cancel it
        @return: None because the action contains all the needed cancellation methods
        """
        pass
