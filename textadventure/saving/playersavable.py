from typing import List

from textadventure.player import Player
from textadventure.saving.savable import Savable
from textadventure.utils import Point


class PlayerSavable(Savable):
    """
    Note that this class does not represent the player's data accurately. It just makes sure that the important data \
    is saved/loaded when it's before_save and on_load methods are called

    This class is not meant to be extended; make your own Savable class. It's not that hard
    """

    def __init__(self):
        super().__init__()
        self.point = Point(0, 0)
        self.items = []
        self.name = None

    def __str__(self):
        return "PlayerSavable(point:{},items:{},name:{})".format(self.point, self.items, self.name)

    def __update_variables(self, player: Player):
        self.point = player.location.point
        self.items = list(player.items)
        self.name = player.name

    def __apply_variables(self, player: Player, handler):
        player.location = handler.get_point_location(self.point)
        player.items.clear()
        player.items.extend(self.items)
        player.name = self.name

    def before_save(self, player: Player, handler):
        self.__update_variables(player)
        for item in self.items:
            item.before_save(player, handler)

    def on_load(self, player: Player, handler):
        self.__apply_variables(player, handler)
        for item in self.items:
            item.on_load(player, handler)
