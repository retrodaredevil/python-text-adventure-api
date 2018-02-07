from typing import Any, TYPE_CHECKING

from textadventure.saving.savable import Savable
from textadventure.utils import Point

if TYPE_CHECKING:
    from textadventure.player import Player
    from textadventure.handler import Handler


class PlayerSavable(Savable):
    """
    Note that this class does not represent the player's data accurately. It just makes sure that the important data \
    is saved/loaded when it's before_save and on_load methods are called

    If you are inheriting this class, use the _update_variables and _apply_variables methods to make sure custom
    variables (variables you instantiated in your constructor) are updated and applied. Make sure to call super()
    """

    def __init__(self):
        super().__init__()
        self.point = Point(0, 0)
        self.items = []
        self.handled_savables = []
        self.name = None

    def __str__(self):
        return "PlayerSavable(point:{},items:{},name:{})".format(self.point, self.items, self.name)

    def _update_variables(self, player: 'Player'):
        """Called when saving. Use to make sure all variables are up to date"""
        self.point = player.location.point
        self.items = list(player.items)
        self.name = player.name
        for o in player.handled_objects:
            if isinstance(o, Savable):
                self.handled_savables.append(o)

    def _apply_variables(self, player: 'Player', handler):
        """Called when loading. Use to apply the data that is being loaded."""
        player.location = handler.get_point_location(self.point)

        player.items.clear()  # TODO decide if we want to just say player.items = ... or keep it this way
        player.items.extend(self.items)

        player.name = self.name

        player.handled_objects.clear()
        player.handled_objects.extend(self.handled_savables)

    def before_save(self, source: Any, handler: 'Handler'):
        # assert isinstance(source, Player), "The only thing that should be handling this is a player"
        self._update_variables(source)
        for item in self.items:
            item.before_save(source, handler)

        for o in self.handled_savables:
            o.before_save(source, handler)

    def on_load(self, source: Any, handler: 'Handler'):
        # assert isinstance(source, Player), "The only thing that should be handling this is a player"
        self._apply_variables(source, handler)
        for item in self.items:
            item.on_load(source, handler)

        for o in self.handled_savables:
            o.on_load(source, handler)
