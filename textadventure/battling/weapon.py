from textadventure.handler import Handler
from textadventure.item import Item
from textadventure.player import Player


class Weapon(Item):
    """
    All weapons should be items because they are going to be in your inventory and making them items makes it easier\
        to change data for the item. Ex: A Weapon could be your right fist, but if you use the command use right fist,\
        it would do something. That's why all Weapons will be items. Thanks for listening.

    Remember, by default, everything is set to false and you need to override all methods except listen (since you \
        don't need that) By default can_take and can_put return CanDo s with True values at [0]
    """

    def __init__(self, name):
        super().__init__(name, True)

    # NOTDO I had the idea that I'd put methods here to damage entities or something. I'll be using the MoveOption class

    def can_take(self, player: Player):
        return True, "You can take this"

    def can_put(self, player: Player):
        return True, "I guess you can put this. You may need it tho."

    def listen(self, handler: Handler, player: Player):
        raise NotImplementedError("Can't listen to a weapon")
