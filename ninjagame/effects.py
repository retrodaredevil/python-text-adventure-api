from typing import Tuple

from textadventure.battling.actions import DamageAction
from textadventure.battling.damage import WeaponHPDamage
from textadventure.battling.effect import PropertyEffect
from textadventure.battling.move import Target


class SwordDamageAlter(PropertyEffect):
    def __init__(self, user: Target, sword_move_type_effectiveness: Tuple[float, float, float]):
        """
        @param sword_move_type_effectiveness: [Slash multiplier, slam multiplier, stab multiplier]
        """
        super().__init__(user, "SwordDamageAlter")
        self.sword_move_type_effectiveness = sword_move_type_effectiveness

    def on_damage(self, damage_action: DamageAction):
        from ninjagame.moves import SwordMove
        if isinstance(damage_action.cause_object, SwordMove) and isinstance(damage_action.damage, WeaponHPDamage):
            # from damage_action.cause_object
            sword_move = damage_action.cause_object
            index = sword_move.move_type.value[1]
            multiplier: float = self.sword_move_type_effectiveness[index]
            # from damage_action.damage
            damage: WeaponHPDamage = damage_action.damage

            # now, let's change the damage using the multiplier
            damage.multiplier_list.append(multiplier)

        return []

