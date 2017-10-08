from textadventure.action import Action
from textadventure.entity import HostileEntity
from textadventure.manager import Manager


class HostileEntityManager(Manager):
    def __init__(self):
        pass

    def update(self, handler):
        pass

    def on_action(self, handler, action: Action):
        from textadventure.location import GoAction
        # print("we got and action: {}".format(action)) works
        if isinstance(action, GoAction):
            for entity in action.previous_location.get_entities(handler):
                if isinstance(entity, HostileEntity):
                    can_pass = entity.can_entity_pass(action.entity)
                    if not can_pass[0]:
                        action.can_do = can_pass
                        return
