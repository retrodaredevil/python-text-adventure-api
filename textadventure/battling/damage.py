from abc import ABC, abstractmethod


class Damage(ABC):  # TODO this code and this class doesn't do anything right now

    @abstractmethod
    def damage(self, entity):
        """@returns a list of DamageOutcome s
        should not filter the list of DamageOutcomes based on the effects of the entity (like if the entity has an invincibility effect)
        (It should change the values of damage based on things like health, max_health etc (if needed))
        """
        pass

