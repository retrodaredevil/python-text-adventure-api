from textadventure.action import Action
from textadventure.manager import Manager


class HostileEntityManager(Manager):
    def __init__(self):
        pass

    def update(self, handler):
        pass

    def on_action(self, handler, action: Action):
        from textadventure.entity import EntityAction
        if isinstance(action, EntityAction):
            pass
