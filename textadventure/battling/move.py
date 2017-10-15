import typing
from abc import ABC, abstractmethod
from typing import List, Dict, Union

from textadventure.battling.team import Team
from textadventure.entity import Entity
from textadventure.utils import CanDo

if typing.TYPE_CHECKING:  # if removed, will cause type errors
    from textadventure.battling.choosing import MoveOption, MoveChooser
    from textadventure.battling.battle import Battle


class Target:
    """
    An object that stores information on the current turn and what moves it can use

    Later, if the api is changed for a pokemon like game, we want to make sure this class doesn't heavily rely on
        Entity when Entity could be changed drastically for a Pokemon game. Just a thought for future maintainability
    """

    def __init__(self, entity: Entity, team: Team, move_chooser: 'MoveChooser', turn_number: int):
        """

        @param entity: The entity
        @param team: The team that the entity is on
        """
        from textadventure.battling.effect import Effect  # to avoid import errors
        self.entity = entity
        self.team = team
        self.move_chooser = move_chooser
        self.turn_number = turn_number  # turn object not passed to avoid import errors and avoid passing a reference\
        #  of self somehow to the Turn object

        self.effects: List[Effect] = []

        self.moves_left = 1  # one move per turn (Duh!)
        self.used_moves: List[Move] = []
        self.outcomes: Dict[Move, bool] = {}
        """Tells whether or not a certain move hit this Target object."""

    def set_outcome(self, move: 'Move', did_hit: bool):  # maybe change the did_hit to something other than bool later
        self.outcomes[move] = did_hit

    def did_hit(self, key: Union['Move', Entity, 'Target']):
        if isinstance(key, Move):
            return self.outcomes[key]
        elif isinstance(key, Entity) or isinstance(key, Target):
            is_entity = isinstance(key, Entity)  # if False, then key is a Target
            for k, value in self.outcomes.items():
                if (is_entity and k.user.entity == key) or (not is_entity and k.user == key):
                    return value

            return None
        else:
            raise ValueError("key must be an instance of a Move or an Entity object. You must have type checks off.")

    def get_move_options(self) -> List['MoveOption']:
        """
        Should only be used by MoveChooser to tell what options there are for moves
        @return: A list of MoveOptions that, by default, is based on the items that the Target currently has
        """
        from textadventure.battling.weapon import Weapon
        r = []
        for item in self.entity.items:
            if isinstance(item, Weapon):
                move_option = item.move_option
                if move_option is not None:
                    r.append(move_option)

        return r

    def create_target_next_turn(self, turn_number: int) -> 'Target':
        """
        Creates a new Target that should be used on the next turn
        @return: The Target to use for the next turn
        """
        target = Target(self.entity, self.team, self.move_chooser, turn_number)
        return target


class Turn:
    def __init__(self, number: int, targets: List[Target]):
        self.number = number
        self.targets = targets  # remember, this is stored like this because a Team has entities as members

        self.is_started = False
        self.is_doing = False
        self.is_done = False

        self.chosen_moves: Dict[Target, Move] = {}  # note that this has nothing to do with move options. Let \
        # MoveChooser handle that stuff

    def start(self, battle: 'Battle'):
        self.is_started = True

    def update(self, battle: 'Battle'):  # should be called by the Battle class
        do_turn = True
        for target in self.targets:
            move = self.chosen_moves[target]
            if move is None:
                do_turn = False
                move = target.move_chooser.get_move(self, target)  # note that this is NOT a MoveOption
                # the move is what the move_chooser returned at we aren't going to question that.
                if move is not None:  # also should probably check if it's None first (Maybe they haven't decided)
                    self.chosen_moves[target] = move

        if do_turn:
            self._do_turn(battle)
            self._on_end(battle)

    def _do_turn(self, battle: 'Battle'):
        self.is_doing = True  # set to True because turn is actually going on now

        moves: List[Move] = []
        for target in self.targets:
            move = self.chosen_moves[target]  # get their chosen move
            moves.append(move)
        moves.sort(key=lambda k: k.priority)  # sort by priority

        for move in moves:  # we will call before turn
            # in separate for loop than the other one because we want before_turn to be called before move.do_move
            for effect in move.user.effects:
                # effect.can_choose let the MoveChooser handle this (We don't even have the MoveOption anyway)
                effect.before_turn(self, move)  # call before turn (And before all moves
        for move in moves:  # now we will call do_move

            can_move: CanDo = (True, "By default, you can move. An effect might say otherwise")
            for effect in move.user.effects:
                can_move = effect.can_move(move)
                if not can_move[0]:
                    break  # another effect might say you can use it, so we want to make sure this one is 'heard'

            # TODO make can_move like an outcome and 'combine' it with do_move's outcome idk
            move.do_move(self)  # actually do the move
            for effect in move.user.effects:
                effect.after_move(self, move)  # call after move
        for move in moves:  # now we will call after turn
            for effect in move.user.effects:
                effect.after_turn(self, move)

        # now we are done with calling effects and all the moves have been invoked
        # lets let _on_end handle the ending of a turn. We're done here

    def _on_end(self, battle: 'Battle'):
        for target in self.targets:
            for effect in list(target.effects):  # get a copy of the list and remove from target.effects
                stay = effect.should_stay(self)  # this turn is now pretty much the previous turn
                if not stay:
                    target.effects.remove(effect)

        self.is_done = True


class Move(ABC):
    def __init__(self, priority: int, user: Target, targets: List[Target]):
        """

        @param priority: The priority of the move where it will move first if it is lower
        @param user: The user of the move
        @param targets: The targets the user is targeting
        """
        self.priority = priority
        self.user = user
        self.targets = targets

    @abstractmethod
    def do_move(self, turn: Turn):
        pass





def main():
    print("test")  # used to make sure that there are no "not defined" errors with the types


if __name__ == '__main__':
    main()
