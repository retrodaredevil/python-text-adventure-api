from abc import ABC, abstractmethod

from textadventure.battling.battle import Battle
from textadventure.battling.effect import Effect
from textadventure.battling.move import Target
from textadventure.battling.outcome import OutcomePart
from textadventure.battling.weapon import Weapon


class Damage(ABC):  # like an interface
    """
    A class that represents and performs one type of damage. For instance, this class could affect the health of an \
        entity but if it does that, it should not add an effect to the entity, you should have a separate Damage class\
        for that.
    A Damage object could actually heal, but for the majority of the classes that inherit Damage, it will damage.
    Note that creating a class that inherits this may not always be a great idea because the code that manages the \
        common and already defined subclasses of Damage, won't manage your new, custom Damage subclass.
    """

    def __init__(self, damager: Target, target: Target):
        """
        @param damager: The Target that's performing the Damage
        @param target: The Target that's receiving the Damage
        """
        self.damager = damager
        self.target = target

    @abstractmethod
    def damage(self, battle: Battle) -> OutcomePart:
        """
        The method that should be called to actually DO the damage (or whatever this class does)
        @param battle: The Battle object which the damager and target are currently in
        @return: An OutcomePart that will be broadcasted
        """
        pass


class WeaponDamage(Damage):  # like an interface
    """
    A funky class that is meant to be an interface like class and should be used in a subclass of Damage when the \
        thing causing the Damage is a weapon.
    To call the __init__, you should use WeaponDamage.__init__(self, weapon)
    Note WeaponDamage's init method doesn't call the superclass's init
    """
    def __init__(self, weapon: Weapon):
        self.weapon = weapon


class HPDamage(Damage):
    def __init__(self, damager: Target, target: Target, hp_change: int):
        """
        @param hp_change: The integer amount to change the hp by. A positive number will heal while a negative number\
                            will damage
        """
        super().__init__(damager, target)
        self.hp_change = hp_change

    def damage(self, battle: Battle):
        health = self.target.entity.health
        health.change_by(self.hp_change)


class EffectDamage(Damage):
    def __init__(self, damager: Target, target: Target, effect: Effect):
        super().__init__(damager, target)
        self.effect = effect

    def damage(self, battle: Battle):
        pass


class WeaponHPDamage(HPDamage, WeaponDamage):
    def __init__(self, damager: Target, target: Target, hp_change: int, weapon: Weapon):
        super().__init__(damager, target, hp_change)
        WeaponDamage.__init__(self, weapon)


class WeaponEffectDamage(EffectDamage, WeaponDamage):
    def __init__(self, damager: Target, target: Target, effect: Effect, weapon: Weapon):
        super().__init__(damager, target, effect)
        WeaponDamage.__init__(self, weapon)


