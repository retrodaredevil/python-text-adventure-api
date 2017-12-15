from ninjagame.effects import SwordDamageAlter
from ninjagame.entites import NinjaEntity
from textadventure.battling.managing import PropertyEffectManager
from textadventure.battling.move import Target


class NinjaGamePropertyManager(PropertyEffectManager):

    def create_effects(self, target: Target):
        r = []
        entity = target.entity
        if isinstance(entity, NinjaEntity):
            # Add an effect to all NinjaEntities to alter how effective a sword is depending on the SwordMoveType
            r.append(SwordDamageAlter(entity, (1.2, 0.5, 1)))  # slashes are effective, slams aren't, and stabs -normal
        return r
