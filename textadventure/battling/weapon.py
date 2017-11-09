from typing import Optional, List

from textadventure.battling.choosing import MoveOption
from textadventure.handler import Handler
from textadventure.item import Item
from textadventure.player import Player


class Weapon(Item):
    """
    All weapons should be items because they are going to be in your inventory and making them items makes it easier\
        to change data for the weapon. Ex: A Weapon could be your right fist, but if you use the command use right fist,\
        it would do something. That's why all Weapons will be items. Thanks for listening.

    A weapon can also be something like a potion. Basically, a weapon is just something that you use in a battle

    Remember, by default, everything is set to false and you need to override all methods except listen (since you \
        don't need that) By default can_take and can_put return CanDo s with True values at [0]
    """

    def __init__(self, name: str, move_options: Optional[List[MoveOption]] = None):
        """

        :param name: The name of the weapon
        :param move_options: A list of MoveOptions or None which will set self.move_options to an empty list
        """
        super().__init__(name, True)
        if move_options is None:
            move_options = []
        self.move_options: List[MoveOption] = move_options

    def can_take(self, player: Player):
        return True, "You can take this"

    def can_put(self, player: Player):
        return True, "I guess you can put this. You may need it tho."

    def listen(self, handler: Handler, player: Player):
        raise NotImplementedError("Can't listen to a weapon")
