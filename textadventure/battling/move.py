from abc import ABC, abstractmethod
from enum import Enum, unique, auto
from typing import List, Dict, Union, Optional

from textadventure.battling.team import Team
from textadventure.entity import Entity
from textadventure.utils import CanDo


class Target:
    """
    An object that stores information on the current turn and what moves it can use
    """
    def __init__(self, entity: Entity, team: Team):
        """

        @param entity: The entity
        @param team: The team that the entity is on
        """
        self.entity = entity
        self.team = team
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


class MoveOption(ABC):  # like an interface

    @abstractmethod
    def can_use_move(self, user: Entity) -> CanDo:
        pass

    @abstractmethod
    def can_choose(self, user: Entity, targets: List[Target]) -> CanDo:
        pass


class Move(ABC):

    def __init__(self, user: Target):
        self.user = user

    @abstractmethod
    def do_move(self, user: Entity, targets: List[Target]):
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
