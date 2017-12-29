import warnings
from abc import abstractmethod
from typing import List, Tuple, TYPE_CHECKING

from textadventure.action import Action
from textadventure.battling.battle import Battle
from textadventure.battling.move import Target
from textadventure.entity import HostileEntity, Entity, CommunityHostileEntity
from textadventure.handler import Handler
from textadventure.manager import Manager

if TYPE_CHECKING:
    from textadventure.battling.team import Team
    from textadventure.battling.effect import Effect

"""
We can import all this stuff because none of it should be referencing anything from the battle package \
    except battle.py but that won't reference this file anyway
If you do import this package, it is recommended to import locally
"""


class BattleManager(Manager):
    """
    A class that makes handles all the battles. And allows the battle api to function
    Note that when adding a battle using add_battle, it will not automatically start the battle (has_started is not \
        set) However, once the battle is updated and

    Note: You must also add HostileEntityManager as a manager or it will not stop players from passing if there are HEs
    """

    def __init__(self):
        super().__init__()
        self.active_battles = []

        self.stop_entities_from_leaving_location = (True, True)
        """Of the type: Tuple[bool, bool] where [0] represents whether or not entities changing locations should\ 
        be stopped and [1] is only used if [0] is True. [1] is True when the entity should be stopped even if the\ 
        battle hasn't started. By default, both are True."""

    def update(self, handler: Handler):
        for battle in list(self.active_battles):
            if battle.should_update():
                battle.update(handler)
            if battle.has_ended:
                self.active_battles.remove(battle)  # the battle has ended so remove it

    def add_battle(self, battle: Battle):
        """
        Adds a battle to the list of active_battles. If the battle has not started, it will not start the battle
        :param battle: The battle you want to add
        """
        self.active_battles.append(battle)

    def get_battles(self, entity: Entity) -> List[Battle]:
        """
        This gets a list of current battles the entity is currently in. It returns a list because it is possible for\
            someone to be in multiple battles at once. (Usually only one should be started)
            This is kept like this just in case people for whatever reason add an entity to multiple battles.
        :param entity: The entity that you are trying to find the battles that it's in
        :return: A list of the current battles the entity is in
        """
        r = []
        for battle in self.active_battles:
            if battle.get_team(entity) is not None:
                r.append(battle)

        return r

    def on_action(self, handler: Handler, action: Action):
        from textadventure.location import GoAction
        if isinstance(action, GoAction):
            if not action.can_do[0]:
                return  # already cancelled so don't mess with it
            if not self.stop_entities_from_leaving_location[0]:
                return  # stopping entities is not wanted here
            # now we know stopping entities from changing locations while in battle is wanted
            battles = self.get_battles(action.entity)
            for battle in battles:
                if battle.is_going_on() or (not battle.has_started and self.stop_entities_from_leaving_location[1]):
                    action.can_do = (False, "You can't leave! You've got to stay and fight!")
                    return  # we cancelled the action so we good - possibly change to "break" later on


class HostileEntityManager(Manager):
    """
    A Manager that stops players from passing if there's a Hostile Entity in their way.
    """

    def __init__(self):
        pass

    def update(self, handler: Handler):
        pass

    def on_action(self, handler: Handler, action: Action):
        from textadventure.location import GoAction
        from textadventure.battling.actions import BattleEnd

        if isinstance(action, GoAction):
            if not action.can_do[0]:
                return  # already cancelled, so don't mess with it
            for entity in action.previous_location.get_entities(handler):  # go through all entities at current location
                if isinstance(entity, HostileEntity):  # if it's a HostileEntity
                    can_pass = entity.can_entity_pass(action.entity)  # check if the hostile entity wants to stop them
                    if not can_pass[0]:  # if the hostile entity wants to stop them, V
                        action.can_do = can_pass  # set the action's can_do to a CanDo with a [0] value of False
                        return  # we don't need to do anything else

        elif isinstance(action, BattleEnd):  # this part handles CommunityHostileEntities
            # future maintainers, this is gonna be a lot of for loops so get used to it
            # print("BattleEnd called")
            battle = action.battle
            winning_team = action.winning_team
            community_hostiles = []  # type List[Tuple[CommunityHostileEntity, 'Team']]
            for team in battle.teams:
                for entity in team.members:
                    if isinstance(entity, CommunityHostileEntity):
                        community_hostiles.append((entity, team))

            # now community_hostiles has a list of tuples with each CommunityHostileEntity
            for hostile_tuple in community_hostiles:
                hostile = hostile_tuple[0]
                hostile_team = hostile_tuple[1]
                for team in battle.teams:
                    if team == hostile_team:  # now the members can't be on the same team
                        continue
                    for entity in team.members:
                        if winning_team == team:  # entity has beaten hostile
                            hostile.entities_lost_to.append(entity)
                            # print("Appended to lost_to: {}".format(entity))
                        elif winning_team == hostile_team:  # extra elif that will only be false if more than 3 teams
                            hostile.entities_won_against.append(entity)
                            # print("Appended to won_to: {}".format(entity))
                        else:
                            print("This shouldn't be called unless there are more than 2 teams")


class DamageActionManager(Manager):
    """
    Simple manager that is used to do different things when something damages something else.

    By default, it calls on_damage for each effect that was involved in damaging or being damaged. (It won't call\
    the effects for a teammate if the teammate didn't do anything
    """
    def __init__(self):
        pass

    def update(self, handler: Handler):
        pass

    def on_action(self, handler: Handler, action: Action):
        from textadventure.battling.actions import DamageAction
        if isinstance(action, DamageAction):
            damage = action.damage
            to_alert = [damage.target]  # TODO If we have multiple entities on a team, we may need to change the \
            #       implementation of creating this list
            if isinstance(damage.damager, Target):
                to_alert.append(damage.damager)

            for target in to_alert:
                for effect in target.effects:
                    outcomes = effect.on_damage(action)
                    if outcomes is None:
                        warnings.warn("List of outcomes from class {} are None.".format(type(effect)))
                    action.outcome_parts.extend(outcomes)


class PropertyEffectManager(Manager):
    """
    An abstract class that should be inherited by a custom class where its create_effects method adds different\
        PropertyEffects to customize the gameplay
    """

    def update(self, handler: 'Handler'):
        pass

    def on_action(self, handler: 'Handler', action: Action):
        from textadventure.battling.actions import BattleStart
        if isinstance(action, BattleStart):
            battle = action.battle
            turn = battle.current_turn
            assert turn is not None, "When invoking a BattleStart action, you need to initialize current_turn"
            for target in turn.targets:
                effects = self.create_effects(target)
                target.effects.extend(effects)

    @abstractmethod
    def create_effects(self, target: Target) -> List['Effect']:
        """
        Called whenever a battle starts. Should be used whenever you want to add PropertyEffects

        :param target: The target that you will add effects to
        :return: All of the PropertyEffects (and or Effects) you want to add to target
        """
        pass
