from typing import Tuple

from ninjagame.moves import SwordMove
from textadventure.battling.actions import DamageAction
from textadventure.battling.damage import WeaponHPDamage
from textadventure.battling.effect import PropertyEffect
from textadventure.entity import Entity


class SwordDamageAlter(PropertyEffect):
    """
    Simple PropertyEffect that allows you to add
    """
    def __init__(self, user: Entity, sword_move_type_effectiveness: Tuple[float, float, float]):
        """
        :param sword_move_type_effectiveness: [Slash multiplier, slam multiplier, stab multiplier]
        """
        super().__init__(user, "SwordDamageAlter")
        self.sword_move_type_effectiveness = sword_move_type_effectiveness

    def on_damage(self, damage_action: DamageAction):
        damage = damage_action.damage
        target = damage.target
        # print(f"Got on_damage with user.entity: {self.user.entity}, target.entity: {target.entity}")
        if target.entity != self.user:
            # remember, we need this if statement, because this method gets called on all damages
            return []  # we want the person receiving the damage to be the person that has the effect

        if isinstance(damage_action.cause_object, SwordMove) and isinstance(damage, WeaponHPDamage):
            # section using damage_action.cause_object
            sword_move = damage_action.cause_object
            index = sword_move.move_type.value[1]  # SwordMoveType's value is a tuple with [1] being the index
            multiplier: float = self.sword_move_type_effectiveness[index]  # noinspection PyTypeChecker
            # section using damage_action.damage
            damage: WeaponHPDamage = damage_action.damage

            # now, let's change the damage using the multiplier
            damage.multiplier_list.append(multiplier)

        return []
