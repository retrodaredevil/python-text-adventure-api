from typing import List

from ninjagame.items import Sword
from ninjagame.moves import SwordMove
from textadventure.battling.choosing import MoveOption, TargetingOption, Targetability
from textadventure.battling.move import Target
from textadventure.battling.weapon import Weapon
from textadventure.item import Item
from textadventure.utils import CanDo


class SimpleMoveOption(MoveOption):
    CAN_CHOOSE_TARGETS: CanDo = (True, "You are able to choose all of these targets.")
    CANT_TARGET_SELF: CanDo = (False, "You can't target yourself!")
    CANT_TARGET_TEAM: CanDo = (False, "You can't target your teammates!")
    CANT_TARGET_ENEMIES: CanDo = (False, "You can't target enemies with this move.")

    def __init__(self, targeting_option: TargetingOption):
        super().__init__()
        self._targeting_option = targeting_option

    def can_use_move(self, user: Target):
        return True

    def get_targeting_option(self, user: Target):
        return self._targeting_option

    def can_choose_targets(self, user: Target, targets: List[Target]):
        rec = self.get_targeting_option(user)
        unable = Targetability.NOT_ABLE
        for target in targets:
            if target == user and rec.user == unable:
                return self.__class__.CANT_TARGET_SELF
            elif target.team == user.team and rec.other_teammates == unable:
                return self.__class__.CANT_TARGET_TEAM
            elif target.team != user.team and rec.enemies == unable:
                return self.__class__.CANT_TARGET_ENEMIES

        return self.__class__.CAN_CHOOSE_TARGETS


class WeaponMoveOption(SimpleMoveOption):  # abstract
    def __init__(self, weapon: Weapon, targeting_option: TargetingOption):
        super().__init__(targeting_option)
        self.weapon = weapon

    def __str__(self):
        return str(self.weapon)


class SwordMoveOption(WeaponMoveOption):
    def __init__(self, sword: Sword, number_of_targets: int):
        super().__init__(sword, TargetingOption(Targetability.NOT_ABLE, Targetability.NOT_RECOMMENDED,
                                                Targetability.RECOMMENDED, number_of_targets))
        self.weapon = sword

    def create_move(self, user: Target, targets: List[Target]):
        return SwordMove(user, targets, self.weapon)
