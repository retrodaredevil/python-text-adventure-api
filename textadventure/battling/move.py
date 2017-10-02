from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional

from textadventure.battling.team import Team
from textadventure.entity import Entity
from textadventure.utils import CanDo


class Target:
    """
    An object that stores information on the current turn and what moves it can use
    """

    def __init__(self, entity: Entity, team: Team, turn_number: int):
        """

        @param entity: The entity
        @param team: The team that the entity is on
        """
        self.entity = entity
        self.team = team
        self.turn_number = turn_number

        self.moves_left = 1  # one move per turn (Duh!)
        self.used_moves: List[Move] = []
        self.outcomes: Dict[Move, bool] = {}

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

    def create_target_next_turn(self, turn_number: int) -> 'Target':
        """
        Creates a new Target that should be used on the next turn
        @return: The Target to use for the next turn
        """
        target = Target(self.entity, self.team, turn_number)
        return target


class Turn:
    def __init__(self, number: int, targets: List[Target]):
        self.number = number
        self.targets = targets


class Move(ABC):

    def __init__(self, user: Target):
        self.user = user

    @abstractmethod
    def do_move(self, turn: Turn, user: Entity, targets: List[Target]):
        pass


class MoveOption(ABC):  # like an interface

    @abstractmethod
    def can_use_move(self, user: Target) -> CanDo:
        """

        @param user: The user that will end up using this Move
        @return: A CanDo tuple where [0] is a boolean value that determines whether or not you can use this move
        """
        pass

    @abstractmethod
    def can_choose(self, user: Target, targets: List[Target]) -> CanDo:
        """

        @param user: The user that will end up using this Move
        @param targets: The list of targets that the player is trying to target
        @return: A CanDo tuple where [0] is a boolean value that determines whether or not the user can target targets
        """
        pass

    @abstractmethod
    def create_move(self, user: Target, targets: List[Target]):
        pass


class MoveChooser(ABC):
    """
    An object that is usually created for each entity in the battle. When a new Target is created for the entity\
        stored inside this object, that Target will be passed to get_move whenever get_move is called
    """

    def __init__(self, entity: Entity):
        self.entity = entity

    @abstractmethod
    def get_move(self, user: Target) -> Optional[Move]:
        """
        @param user: The target that will be using the returned move. user.entity is always equal to this class's entity
        @return: The chosen move or None if no Move has been chosen yet
        """
        pass


def main():
    print("test")  # used to make sure that there are no "not defined" errors with the types


if __name__ == '__main__':
    main()
