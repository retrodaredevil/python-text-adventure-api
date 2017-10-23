import typing

from textadventure.action import Action
from textadventure.battling.managing import BattleManager
from textadventure.battling.team import Team
from textadventure.entity import EntityActionToEntity, Entity

if typing.TYPE_CHECKING:
    from textadventure.battling.battle import Battle


"""
A file dedicated to define implementations of the Action class related to the battling api
"""


class BattleEnd(Action):
    """
    An Action that may have unexpected results when cancelling. Basically an event that tells you when the Battle ends.
    """
    def __init__(self, battle: 'Battle'):
        super().__init__()
        self.battle: 'Battle' = battle

    def _do_action(self, handler):
        self.battle.has_ended = True
        return self.can_do


class EntityChallengeAction(EntityActionToEntity):
    def __init__(self, entity: Entity, asked_entity: Entity):
        super().__init__(entity, asked_entity)

    def _do_action(self, handler):
        from textadventure.battling.battle import Battle
        battle = Battle([Team([self.entity]), Team([self.asked_entity])])
        manager: BattleManager = handler.get_managers(BattleManager, 1)[0]
        manager.add_battle(battle)
        return self.can_do
