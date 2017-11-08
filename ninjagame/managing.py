from ninjagame.effects import SwordDamageAlter
from ninjagame.entites import NinjaEntity
from textadventure.battling.managing import PropertyEffectManager
from textadventure.battling.move import Target


class NinjaGamePropertyManager(PropertyEffectManager):

    def create_effects(self, target: Target):
        r = []
        entity = target.entity
        if isinstance(entity, NinjaEntity):
            # print("Added SwordDamageAlter to : {}".format(entity)) works
            r.append(SwordDamageAlter(entity, (1.2, 0.5, 1)))
        return r
