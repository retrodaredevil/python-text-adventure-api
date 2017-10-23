from textadventure.action import Action
from textadventure.entity import EntityActionToEntity
from textadventure.handler import Handler
from textadventure.manager import Manager


"""
A class for useful and usually needed Managers that help the game do what it should.
The defined classes, usually shouldn't be referenced in the code and if they are, they should be imported locally
"""


class EntityActionToEntityManager(Manager):
    def __init__(self):
        pass  # calling super().__init__() raises TypeError

    def update(self, handler: Handler):
        pass

    def on_action(self, handler: Handler, action: Action):
        if isinstance(action, EntityActionToEntity):
            can_do = action.asked_entity.can_do_action(handler, action)
            if not can_do[0]:
                action.can_do = can_do
                #  action.entity.send_message(can_do[1]) we don't need this because EntityAction handles this

