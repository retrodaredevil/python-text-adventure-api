from abc import ABC, abstractmethod
from typing import Union, List

from textadventure.battling.battle import Battle
from textadventure.battling.effect import Effect
from textadventure.battling.move import Target
from textadventure.battling.outcome import OutcomePart, HealthChangeOutcome
from textadventure.battling.weapon import Weapon


"""
Please be careful when using these classes, some use multiple inheritance and don't use the super() method \
    The reason for this is to make sure that the right __init__ method gets called. 
    Instead, most classes just call ClassName.__init__(self, parameters...)
"""


class Damage(ABC):  # like an interface
    """
    A class that represents and performs one type of damage. For instance, this class could affect the health of an \
        entity but if it does that, it should not add an effect to the entity, you should have a separate Damage class\
        for that.
    A Damage object could actually heal, but for the majority of the classes that inherit Damage, it will damage.
    Note that creating a class that inherits this may not always be a great idea because the code that manages the \
        common and already defined subclasses of Damage, won't manage your new, custom Damage subclass.
    """

    def __init__(self, damager: Union[Target, Effect], target: Target):
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
        """
        Note, if you are creating a new instance of THIS class, you are probably doing something wrong,
            @see: WeaponHPDamage
        """
        self.weapon = weapon


class HPDamage(Damage):
    """
    The main type of damage. (Taking away hp)
    """
    def __init__(self, damager: Target, target: Target, hp_change: int):
        """
        If you are using this, you should probably be using WeaponHPDamage or EffectHPDamage unless you know what\
            you're doing
        @param hp_change: The integer amount to change the hp by. A positive number will heal while a negative number\
                            will damage
        """
        Damage.__init__(self, damager, target)
        self.hp_change = hp_change
        self.multiplier_list: List[float] = []
        """Should be appended to when wanting to multiply the damage of hp_change"""

    def _calculate_hp_change(self):
        r = self.hp_change
        for multiplier in self.multiplier_list:
            r *= multiplier
        return r

    def damage(self, battle: Battle):
        from textadventure.entity import Health
        health: Health = self.target.entity.health
        before_health = health.current_health
        health.change_by(self._calculate_hp_change())
        return HealthChangeOutcome(self.target, before_health)


class EffectDamage(Damage):
    """
    The The equivalent of WeaponDamage but for Effects
    """
    def __init__(self, effect: Effect):
        self.effect = effect


class WeaponHPDamage(HPDamage, WeaponDamage):
    """
    A subclass of HPDamage which is usually the damage that should be used most of the time
    Note: So you think you have a bug? Make sure that hp_change is negative. If it isn't, this will heal the target.
    """
    def __init__(self, damager: Target, target: Target, hp_change: int, weapon: Weapon):
        HPDamage.__init__(self, damager, target, hp_change)
        WeaponDamage.__init__(self, weapon)


class EffectHPDamage(HPDamage, EffectDamage):
    """
    The equivalent of WeaponHPDamage, but should be used when the thing causing the damage is the effect
    """
    def __init__(self, damager: Target, target: Target, hp_change: int, effect: Effect):
        HPDamage.__init__(self, damager, target, hp_change)
        EffectDamage.__init__(self, effect)


class WeaponEffectDamage(WeaponDamage):
    """
    A Damage to add the passed effect to the target
    """
    def __init__(self, damager: Target, target: Target, effect: Effect, weapon: Weapon):
        Damage.__init__(self, damager, target)
        WeaponDamage.__init__(self, weapon)  # doesn't call Damage init
        self.added_effect = effect

    def damage(self, battle: Battle):
        self.target.effects.append(self.added_effect)


