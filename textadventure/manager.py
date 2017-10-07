"""
If you are looking for the file that basically handles everything, look at handler.py
The Handler class does stuff with the stuff in this file

A Manager class is kind of like an event handler with an update method

Also, to avoid import errors, this class doesn't import Handler
"""
from abc import ABC, abstractmethod

from textadventure.action import Action


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
    def on_action(self, handler, action: Action):
        """
        Called when an entity tries to do something that needs to be check to make sure they can do that
        @param handler: The Handler object
        @param action: The action that contains all the event information and has the necessary information/methods \
                        to cancel it
        @return: None because the action contains all the needed cancellation methods
        """
        pass
