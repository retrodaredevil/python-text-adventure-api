from abc import ABC, abstractmethod
from typing import List, Dict, Optional, TYPE_CHECKING, Type, TypeVar

from textadventure.battling.outcome import MoveOutcome, OutcomePart  # needed
from textadventure.battling.team import Team
from textadventure.entity import Entity
from textadventure.utils import CanDo

if TYPE_CHECKING:  # if removed, will cause type errors
    from textadventure.battling.choosing import MoveOption, MoveChooser
    from textadventure.battling.battle import Battle
    from textadventure.handler import Handler
    from textadventure.battling.effect import Effect  # to avoid import errors


T = TypeVar('T')


class Target:
    """
    An object that stores information on the current turn and what moves it can use

    Later, if the api is changed for a pokemon like game, we want to make sure this class doesn't heavily rely on
        Entity when Entity could be changed drastically for a Pokemon game. Just a thought for future maintainability
    """

    def __init__(self, entity: Entity, team: Team, move_chooser: 'MoveChooser', turn_number: int):
        """

        :param entity: The entity
        :param team: The team that the entity is on
        """
        self.entity = entity
        self.team = team
        self.move_chooser = move_chooser
        self.turn_number = turn_number  # turn object not passed to avoid import errors and avoid passing a reference\
        #  of self somehow to the Turn object

        self.effects = []
        """Right now, you should just append to this list since we don't have a special method to add effects."""

    def __getitem__(self, item: Type[T]) -> Optional[T]:
        """
        T is recommended to be PropertyEffect and using this to get an effect is not recommended

        :param item: The type of effect to get in the effects list
        :return: The first effect of the exact type 'item' in the self.effects list. Or None if there is none in list
        """
        for effect in self.effects:
            if isinstance(effect, item):
                return effect
        return None

    def get_move_options(self) -> List['MoveOption']:
        """
        Should only be used by MoveChooser to tell what options there are for moves

        :return: A list of MoveOptions that, by default, is based on the items that the Target currently has
        """
        from textadventure.battling.weapon import Weapon
        r = []
        for item in self.entity.items:
            if isinstance(item, Weapon):
                r.extend(item.move_options)

        return r

    def create_target_next_turn(self, previous_turn: 'Turn', turn_number: int) -> 'Target':
        """
        Creates a new Target that should be used on the next turn

        :return: The Target to use for the next turn
        """
        target = Target(self.entity, self.team, self.move_chooser, turn_number)
        for effect in self.effects:
            if effect.should_stay(previous_turn):
                target.effects.append(effect)

        return target


class Turn:
    """
    A class that holds data for a single turn and that contains methods that can be called to initiate the turn.
    The reason this has methods to initiate and to do the turn, is because it should be divided from the Battle class\
        what better way to use all of the data in a turn than using its own methods.
    """
    def __init__(self, number: int, targets: List[Target]):
        self.number = number
        self.targets = targets  # remember, this is stored like this because a Team has entities as members

        self.is_started = False
        self.is_doing = False
        self.is_done = False

        self.chosen_moves = {}
        """Note has nothing to do with move options. This a a Dict[Target, Move] where the key is the target and \
        the value is the move that the target chose"""

    def get_target(self, entity: Entity) -> Optional[Target]:
        for target in self.targets:
            if target.entity == entity:
                return target

        return None

    def start(self, battle: 'Battle'):
        """
        Called when this Turn is being set to the Battle's current turn

        :param battle: The battle handling this Turn object
        """
        self.is_started = True
        battle.broadcast("")  # a new line makes it easier to read
        battle.broadcast_healths()

    def update(self, battle: 'Battle', handler: 'Handler'):  # should be called by the Battle class
        """
        Called by the Battle class every time its update method is called.
        Calling update is how the turn actually works (There is no method to actually DO the turn) (This method will \
            call private methods _do_turn and _on_end
        """
        do_turn = True  # set to False if we can't do the turn because not everyone has already chosen their moves
        for target in self.targets:
            move = self.chosen_moves.get(target, None)
            if move is None:
                do_turn = False
                move = target.move_chooser.get_move(battle, target, self)  # note that this is NOT a MoveOption
                # the move is what the move_chooser returned at we aren't going to question that.
                if move is not None:  # also should probably check if it's None first (Maybe they haven't decided)
                    self.chosen_moves[target] = move

        if do_turn:
            self._do_turn(battle, handler)
            self._on_end(battle)

    def _do_turn(self, battle: 'Battle', handler: 'Handler'):
        self.is_doing = True  # set to True because turn is actually going on now

        moves = []
        for target in self.targets:
            moves.append(self.chosen_moves[target])
        moves.sort(key=lambda m: m.priority + m.calculate_speed())  # sort by priority

        for move in moves:  # we will call before_turn
            # in separate for loop than the other one because we want before_turn to be called before all move.do_move
            for effect in move.user.effects:
                # effect.can_choose_targets let the MoveChooser handle this (We don't even have the MoveOption anyway)
                effect.before_turn(self, move)  # call before turn (And before all moves)

        for move in moves:  # now we will call do_move

            can_move = (True, "By default, you can move. An effect might say otherwise")  # type CanDo
            for effect in move.user.effects:
                can_move = effect.can_move(move)
                if not can_move[0]:
                    break  # another effect might say you can use it, so we want to make sure this one is 'heard'

            if can_move[0]:
                result = move.do_move(battle, handler)  # actually do the move
                outcome = MoveOutcome(can_move)
                outcome.parts.extend(result)
            else:
                outcome = MoveOutcome(can_move)
            for effect in move.user.effects:
                outcome.parts.extend(effect.after_move(self, move, outcome))  # call after move
            # calling this after the loop used to call Effect's after_move because after_move could have done something
            # if we needed to, here is where an Action would go related to the move
            outcome.broadcast(battle)  # TODO somewhere in here we need to create an action

        for move in moves:  # now we will call after_turn
            for effect in move.user.effects:
                MoveOutcome.broadcast_messages(effect.after_turn(self, move), battle)

        # now we are done with calling effects and all the moves have been invoked
        # lets let _on_end handle the ending of a turn. (We don't call it because the method calling this will)

    def _on_end(self, battle: 'Battle'):
        for target in self.targets:
            for effect in list(target.effects):  # get a copy of the list and remove from target.effects
                stay = effect.should_stay(self)  # this turn is now pretty much the previous turn
                if not stay:
                    target.effects.remove(effect)

            target.move_chooser.reset_option()

        self.is_done = True


class Move(ABC):
    def __init__(self, name: str, priority: int, user: Target, targets: List[Target]):
        """

        :param priority: The priority of the move where it will move first if it is lower
        :param user: The user of the moveHello there how are you
        :param targets: The targets the user is targeting
        """
        self.name = name
        self.priority = priority
        self.user = user
        self.targets = targets

    def __str__(self):
        return self.name

    @abstractmethod
    def do_move(self, battle: 'Battle', handler: 'Handler') -> List[OutcomePart]:
        """
        Called when the move should be executed
        Note the order that the returned List at [0] matters because of the order the outcomes will be displayed
        :param handler:
        :param battle: The battle that this move is being used in where current_turn is the current turn that is ongoing
        :return: A list of OutcomeParts (things that this method did)
        """
        pass

    def calculate_speed(self):
        """
        A method that by default, uses the user's speed and nothing else

        :return: Normally a value between -.5 and .5 (And most of the time positive) It represents the number to
        """
        # TODO, is this implemented correctly?
        return 0
