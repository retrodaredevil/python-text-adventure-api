from typing import Any, TYPE_CHECKING

from textadventure.saving.savable import Savable, SaveLoadException

if TYPE_CHECKING:
    from textadventure.handler import Handler


class EntitySavable(Savable):
    def __init__(self):
        super().__init__()
        self.point = None
        self.items = None
        self.name = None
        self.uuid = None

    def __str__(self):
        return self.__class__.__name__ + "(point:{},items:{},name:{},uuid:{})".format(self.point, self.items, self.name,
                                                                                      self.uuid)

    def before_save(self, source: Any, handler: 'Handler'):
        self.point = source.location.point
        self.items = list(source.items)
        self.name = source.name
        self.uuid = source.uuid
        for item in self.items:
            item.before_save(source, handler)

    def on_load(self, source: Any, handler: 'Handler'):
        source.location = handler.get_point_location(self.point)

        source.items.clear()  # TODO in the future, will this cause a side effect?
        source.items.extend(self.items)

        source.name = self.name
        source.uuid = self.uuid

        for item in self.items:
            item.on_load(source, handler)


class PlayerSavable(EntitySavable):
    """
    Note that this class does not represent the player's data accurately. It just makes sure that the important data \
    is saved/loaded when it's before_save and on_load methods are called

    If you are inheriting this class, use the _update_variables and _apply_variables methods to make sure custom
    variables (variables you instantiated in your constructor) are updated and applied. Make sure to call super()
    """

    def __init__(self):
        super().__init__()
        self.handled_savables = None

    def before_save(self, source: Any, handler: 'Handler'):
        super().before_save(source, handler)
        self.handled_savables = []
        for o in source.handled_objects:
            if isinstance(o, Savable):
                self.handled_savables.append(o)

        for o in self.handled_savables:
            o.before_save(source, handler)

        if not handler.player_handler.is_name_valid(self.name):
            raise SaveLoadException("The player does not have a valid name")

    def on_load(self, source: Any, handler: 'Handler'):
        super().on_load(source, handler)
        # assert isinstance(source, Player), "The only thing that should be handling this is a player"
        for o in self.handled_savables:
            o.on_load(source, handler)

        source.handled_objects.clear()
        source.handled_objects.extend(self.handled_savables)
