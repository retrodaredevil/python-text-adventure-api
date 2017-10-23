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
        @return: The message that should be broadcasted or None if this OutcomePart doesn't have anything to say. \
                        (Usually it should have something so say)
        """
        pass


class MoveOutcome:
    """
    Represents a list of messages (OutcomeParts) which will be broadcasted to everyone
    """

    def __init__(self, can_move: CanDo):
        """

        @param can_move: A CanDo tuple representing if the player was able to try to perform the move. This can be \
                         cancelled by effects.
        """
        self.can_move: CanDo = can_move

        self.parts: List[OutcomePart] = []

    def broadcast_messages(self, battle: 'Battle'):
        if not self.can_move[0]:
            battle.broadcast(self.can_move[1])
            return
        for part in self.parts:
            battle.broadcast(part.get_message())


class UseMoveOutcome(OutcomePart):
    def __init__(self, move: 'Move'):
        self.move = move

    def get_targets_object(self):
        """
        Can be overridden to choose what gets said in get_message
        @return: The object to be put in named_variables from the returned get_message
        """
        return self.move.targets

    def get_message(self):
        return Message("{} used {} on {}.", named_variables=[self.move.user, self.move, self.get_targets_object()])


class HealthChangeOutcome(OutcomePart):
    def __init__(self, affected_target: 'Target', before_health: int):
        """
        @param affected_target: The Target that has had its health changed
        @param before_health: The health that the affected_target had before it was affected.
        """
        self.affected_target = affected_target
        self.before_health = before_health

    def get_message(self):
        current_health = self.affected_target.entity.health.current_health
        changed = current_health - self.before_health  # negative means that the affected_target was damaged
        if changed == 0:
            return Message("{} was unaffected.", named_variables=[self.affected_target])
        elif changed > 0:
            return Message("{} was healed by {}hp.", named_variables=[self.affected_target, changed])
        return Message("{} was damaged by {}hp.", named_variables=[self.affected_target, -changed])


class EffectAddedOutcome(OutcomePart):
    def __init__(self, affected_target: 'Target', added_effect: 'Effect'):
        self.affected_target = affected_target
        self.added_effect = added_effect

    def get_message(self):
        return Message("{} was added to {}.", named_variables=[self.added_effect, self.affected_target])
