from abc import abstractmethod

from textadventure.entity import Entity
from textadventure.handler import Handler
from textadventure.item.item import Item
from textadventure.player import Player


NOT_TASTE = "This doesn't taste like anything."
NOT_SMELL = "This doesn't smell like anything."


class StaticObject(Item):

    def __init__(self, name):
        super().__init__(name, False)

    def listen(self, handler: Handler, player: Player):
        pass

    def can_use(self, entity: Entity):
        return False, "You can't use this!"

    def use_item(self, handler: Handler, entity: Entity, does_custom_action=False):
        if not does_custom_action:
            raise Exception("can_use returned False, and we don't know what to do here.")
        return super().use_item(handler, entity, does_custom_action)

    def taste(self, handler: Handler, player: Player):
        player.send_message(NOT_TASTE)

    @abstractmethod
    def feel(self, handler: Handler, player: Player):
        pass

    def smell(self, handler: Handler, player: Player):
        player.send_message(NOT_SMELL)

    @abstractmethod
    def see(self, handler: Handler, player: Player):
        pass


class Tree(StaticObject):

    # TODO implement climbable
    def __init__(self, name="Tree", climbable=False):
        """
        :param name: The name of the Tree which by default is 'Tree'
        """
        super().__init__(name)
        self.climbable = climbable

    def see(self, handler: Handler, player: Player):
        pass

    def feel(self, handler: Handler, player: Player):
        player.send_message("The tree has bark on it and it is very rough.")



