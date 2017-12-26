import typing
from abc import abstractmethod, ABC
from typing import List, Optional

from textadventure.message import Message
from textadventure.utils import CanDo, MessageConstant


if typing.TYPE_CHECKING:
    from textadventure.battling.battle import Battle
    from textadventure.battling.move import Move, Target
    from textadventure.battling.effect import Effect


class OutcomePart(ABC):

    @abstractmethod
    def get_message(self) -> Optional[MessageConstant]:
        """
        Uses the state of this instance to create a message that should be broadcasted to everyone

        :return: The message that should be broadcasted or None if this OutcomePart doesn't have anything to say. \
                        (Usually it should have something so say)
        """
        pass


class MoveOutcome:
    """
    Represents a list of messages (OutcomeParts) which will be broadcasted to everyone

    """

    def __init__(self, can_move: CanDo):
        """
        :param can_move: A CanDo tuple representing if the player was able to try to perform the move. This can be \
                         cancelled by effects.
        """
        self.can_move = can_move

        self.parts = []

    def broadcast(self, battle: 'Battle'):
        if not self.can_move[0]:
            battle.broadcast(self.can_move[1])
            return
        self.__class__.broadcast_messages(self.parts, battle)

    @staticmethod
    def broadcast_messages(messages: List[OutcomePart], battle: 'Battle'):
        for part in messages:
            battle.broadcast(part.get_message())


class UseMoveOutcome(OutcomePart):
    """
    This is more of a special OutcomePart because it should appear pretty much every time a move has been made.
        Usually, for the most part, there shouldn't really be special ones that appear every time because the \
        information displayed may be something that should be displayed with a command.
    """
    def __init__(self, move: 'Move'):
        self.move = move

    def get_targets_object(self):
        """
        Can be overridden to choose what gets said in get_message

        :return: The object to be put in named_variables from the returned get_message
        """
        return self.move.targets

    def get_message(self):
        return Message("{} used {} on {}.", named_variables=[self.move.user.entity, self.move,
                                                             list(map(lambda x: x.entity, self.get_targets_object()))])


class HealthChangeOutcome(OutcomePart):
    def __init__(self, affected_target: 'Target', before_health: int, multiplier: int=1):
        """
        :param affected_target: The Target that has had its health changed
        :param before_health: The health that the affected_target had before it was affected.
        :param multiplier: The multiplier for the amount the health was changed.
        """
        self.affected_target = affected_target
        self.before_health = before_health
        self.multiplier = multiplier

    def get_message(self):
        current_health = self.affected_target.entity.health.current_health
        changed = current_health - self.before_health  # negative means that the affected_target was damaged
        if changed == 0:
            return Message("{} was unaffected.", named_variables=[self.affected_target.entity])
        elif changed > 0:
            return Message("{} was healed by {} hp.", named_variables=[self.affected_target.entity, changed])
        extra = ""
        mult = self.multiplier
        if mult != 1:
            extra += "\n"
            if mult > 1.75:
                extra += "It's super effective!"
            elif mult > 1:
                extra += "It's pretty effective."
            elif mult >= .4:
                extra += "It's not very effective"
            elif mult < 0:
                extra += "The attack decided to do damage instead!"
            else:
                extra += "It didn't do very much at all."
        return Message("{} was damaged by {} hp." + extra, named_variables=[self.affected_target.entity, -changed])


class EffectAddedOutcome(OutcomePart):
    def __init__(self, affected_target: 'Target', added_effect: 'Effect'):
        self.affected_target = affected_target
        self.added_effect = added_effect

    def get_message(self):
        return Message("{} was added to {}.", named_variables=[self.added_effect, self.affected_target.entity])


class EffectRemoveOutcome(OutcomePart):
    def __init__(self, affected_target: 'Target', removed_effect: 'Effect'):
        self.affected_target = affected_target
        self.removed_effect = removed_effect

    def get_message(self):
        return Message("{} was removed from {}.", named_variables=[self.removed_effect, self.affected_target.entity])
