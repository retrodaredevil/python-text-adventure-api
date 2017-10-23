from typing import List

from ninjagame.items import Sword
from textadventure.battling.choosing import MoveOption, TargetingOption
from textadventure.battling.move import Move, Target, Turn
from textadventure.item import Item


class ItemMoveOption(MoveOption):
    def __init__(self, item: Item, targeting_option: TargetingOption):
        self.item = item
        self.targeting_option = targeting_option

    def __str__(self):
        return str(self.item)

    def can_use_move(self, user: Target):
        if self.item not in user.entity.items:
            return False, "Why are you even able to choose this move if you don't have this weapon in your inventory?"
        return True, "Sure you can use this move because you have this weapon"

    def get_targeting_option(self, user: Target):
        return self.targeting_option




class ItemMove(Move):  # abstract
    def __init__(self, priority: int, user: Target, targets: List[Target], item: Item):
        super().__init__(str(item), priority, user, targets)
        self.item = item


class SwordMove(ItemMove):

    def __init__(self, user: Target, targets: List[Target], item: Sword):
        super().__init__(0, user, targets, item)
        self.item = item

    def do_move(self, turn: Turn):
        pass  # TODO
