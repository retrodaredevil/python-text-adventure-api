from abc import ABC, abstractmethod
from enum import unique, Enum
from typing import Type, List

from textadventure.action import Action
from textadventure.holder import Holder
from textadventure.message import Message
from textadventure.utils import MessageConstant, CanDo


class Living(ABC):
    UNKNOWN_LIVING_NAME = "???"

    """
    A Living object unlike an Entity, doesn't have a location which is the biggest difference.
    This will help with the story so you don't have to worry about teleporting an entity just so they can talk

    Basically an entity that the location manipulates and that isn't controlled by outside sources and it's only state\
        is it's name
    """

    def __init__(self, name):
        super().__init__()  # notice that this calls the object init, but it helps with multiple inheritance
        self.name = name

    def get_used_name(self, viewer: 'Living') -> str:
        """
        By default, returns self.name but can be overridden to create the effect that someone doesn't know this person
        @param viewer: The person that the returned name will be showed to
        @return: The string that represents the name the passed 'living' will be shown
        """
        return self.name

    @abstractmethod
    def send_message(self, message):
        """Sends a message to this. Usually a string or Message object"""
        pass

    def tell(self, living: 'Living', message: MessageConstant):
        message = self.get_message(message)
        # if we change the way we do this, like doing this at a later time.
        #   Things could get messed up on the correct name
        message.text = "|" + self.get_used_name(living) + ":| " + message.text
        living.send_message(message)

    def __str__(self):
        """Should be used in Message to replace named_variables with"""
        return self.name

    def get_message(self, message: MessageConstant) -> Message:
        """
        Converts a MessageConstant to a Message
        Makes sure that the passed message value is returned as a Message object
        @param message: The message or string to make sure or change to a Message
        @return: A message object
        """
        if type(message) is str:
            message = Message(message)
        if type(message) is not Message:
            raise TypeError("The type: " + str(type(message)) + " is not supported")
        return message


class Health:
    def __init__(self, current_health: int, max_health: int):
        self.current_health = current_health
        self.max_health = max_health

    def is_fainted(self):
        return self.current_health <= 0

    def is_full(self):
        if self.max_health == 0:
            return False
        return self.current_health == self.max_health


class Entity(Living, Holder):
    def __init__(self, name: str, health: Health, location):
        super().__init__(name)
        from textadventure.location import Location
        self.health = health

        self.location: Location = location
        """
        The location of the entity. Unless, initializing for the first time, you almost should never set this
        By yourself because you probably want to do it with GoAction or something similar that abstracts a few 
        details away.
        """

    # def can_entity_pass(self, entity: 'Entity') -> CanDo:
    #     """ Not going to use this - define in HostileEntity
    #     Called when a entity, usually a player, is trying to go to another location.
    #     This will be called if this entity is in the same location as the entity trying to move to another location
    #     @param entity: The entity trying to move to another location
    #     @return: A CanDo tuple where [0] is a boolean value representing the the entity can pass and if False,\
    #                 [1] is the reason why the entity can't pass. (It will be displayed)
    #     """
    #     return True, "You can pass, a hostile entity might say otherwise, though."

    def damage(self, damage):
        raise Exception("damage method not implemented")


class HostileEntity(Entity):  # abstract
    def __init__(self, name: str, health: Health, location):
        super().__init__(name, health, location)

    @abstractmethod
    def can_entity_pass(self, entity: Entity) -> CanDo:
        """
        Will be used by the HostileEntityManager
        @param entity: The entity that is trying to go to another location
        @return: A CanDo
        """
        # return super().can_entity_pass(entity)
        pass


class SimpleHostileEntity(HostileEntity):

    def __init__(self, name: str, health: Health, location, hostile_to_types: List[Type[Entity]]):
        super().__init__(name, health, location)
        self.hostile_to_types = hostile_to_types

        self.hostile_now = True
        self.can_not_pass: CanDo = (False, Message("You can't pass because {} wants to eat you.",
                                                   named_variables=[self]))

    def can_entity_pass(self, entity: Entity):
        if not self.hostile_now:
            return True, "I'm not hostile right now"

        if self.health.is_fainted():
            return True, "I can't get you because I'm dead."

        for t in self.hostile_to_types:
            if isinstance(entity, t):
                return self.can_not_pass
        return True, "I don't really want to eat you."

    def send_message(self, message):
        pass


class EntityAction(Action):  # abstract
    """
    Used when there's an entity involved in an action (or multiple entities where the entity stored in this class\
        is the one that caused it, usually being the Player (There is no PlayerAction this is it)
    """
    def __init__(self, entity: Entity):
        """

        @param entity: The main entity involved and the one that is basically requesting to do this action
        """
        super().__init__()
        self.entity = entity

    def try_action(self, handler) -> CanDo:
        can_do = super().try_action(handler)
        if not can_do[0]:
            self.entity.send_message(can_do[1])
        return can_do
