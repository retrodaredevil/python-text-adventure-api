from enum import unique, Enum


from textadventure.entity import Entity


# as of right now, there is no regular action class since I don't know what that'd actually do, just EntityActions now


@unique
class EntityActionType(Enum):
    pass


class EntityAction:
    def __init__(self, action_type: EntityActionType, entity: Entity):
        """

        @param action_type: The action type.
        @param entity: The main entity involved and the one that is basically requesting to do this action
        """
        self.action_type = action_type
        self.entity = entity
