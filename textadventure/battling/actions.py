import typing
from typing import Union, List, Any

from textadventure.action import Action
from textadventure.battling.managing import BattleManager
from textadventure.battling.team import Team
from textadventure.entity import EntityActionToEntity, Entity
from textadventure.message import Message

if typing.TYPE_CHECKING:
    from textadventure.battling.battle import Battle
    from textadventure.battling.damage import Damage
    from textadventure.battling.move import Move
    from textadventure.battling.effect import Effect


"""
A file dedicated to define implementations of the Action class related to the battling api
"""


class BattleStart(Action):
    """
    An action that happens when a battle starts. Should not be cancelled
    """
    def __init__(self, battle: 'Battle'):
        super().__init__()
        self.battle: 'Battle' = battle

    def _do_action(self, handler):
        self.battle.has_started = True
        return self.can_do


class BattleEnd(Action):
    """
    An Action that may have unexpected results when cancelling. Basically an event that tells you when the Battle ends.
    """
    def __init__(self, battle: 'Battle', winning_team: Team):
        super().__init__()
        self.battle: 'Battle' = battle
        self.winning_team = winning_team

    def _do_action(self, handler):
        self.battle.has_ended = True
        self.battle.broadcast(Message("{} has won the battle!", named_variables=[self.winning_team]))
        return self.can_do


class EntityChallengeAction(EntityActionToEntity):
    def __init__(self, entity: Entity, asked_entity: Entity):
        super().__init__(entity, asked_entity)

    def _do_action(self, handler):
        from textadventure.battling.battle import Battle
        battle = Battle([Team([self.entity]), Team([self.asked_entity])])
        manager: BattleManager = handler.get_managers(BattleManager, 1)[0]
        manager.add_battle(battle)
        battle.start(handler)
        return self.can_do


class DamageAction(Action):  # DONE create a manager where Effects can handle this Action without creating their own M
    def __init__(self, cause_object: Union['Move', 'Effect', Any], damage: 'Damage', battle: 'Battle'):
        """
        :param cause_object: The object that contains the method that created this. (Almost always a Move or Effect)
        :param damage:
        """
        from textadventure.battling.outcome import OutcomePart
        super().__init__()
        self.cause_object: Union[Move, Effect] = cause_object
        """The object that contains the method that created this. Depending on the implementation or the code you \
        created, this could be None"""
        self.damage = damage
        assert damage is not None
        self.battle = battle

        self.outcome_parts: List[OutcomePart] = []
        """The list of outcome parts that will be appended to when _do_action is called. If a Manager changes \
        something in self.damage, they may want to append an OutcomePart so people know what happened."""

    def _do_action(self, handler):
        self.outcome_parts.append(self.damage.damage(self.battle))  # append a single OutcomePart

