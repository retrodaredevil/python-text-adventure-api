from typing import List, TYPE_CHECKING

from ninjagame.items import Sword, SwordMoveType
from textadventure.battling.actions import DamageAction
from textadventure.battling.battle import Battle
from textadventure.battling.move import Move, Target
from textadventure.battling.outcome import OutcomePart, UseMoveOutcome
from textadventure.item.item import Item
from textadventure.battling.damage import WeaponHPDamage

if TYPE_CHECKING:
    from textadventure.handler import Handler


# noinspection PyAbstractClass
class WeaponMove(Move):  # abstract
    """
    The class that should be used for Moves involving items.
    """

    def __init__(self, priority: int, user: Target, targets: List[Target], item: Item):
        super().__init__(str(item), priority, user, targets)
        self.item = item


class SwordMove(WeaponMove):
    def __init__(self, user: Target, targets: List[Target], item: Sword, move_type: SwordMoveType):
        super().__init__(0, user, targets, item)
        self.item = item
        self.move_type = move_type

        self.name += "'s " + self.move_type.value[0]

    def do_move(self, battle: Battle, handler: 'Handler') -> List[OutcomePart]:
        r = [UseMoveOutcome(self)]  # all we have done is used this move so far

        hp_change = -self.item.sword_type.value[2]  # subtract the amount of hp the sword_type takes away
        for target in self.targets:  # attack all the targets (usually just one)
            damage = WeaponHPDamage(self.user, target, hp_change, self.item)

            action = DamageAction(self, damage, battle)
            handler.do_action(action)
            action.try_action(handler)
            r.extend(action.outcome_parts)

        return r
