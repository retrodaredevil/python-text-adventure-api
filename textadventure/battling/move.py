from abc import ABC, abstractmethod
from enum import Enum, unique, auto
from typing import List, Dict, Union

from textadventure.battling.team import Team
from textadventure.entity import Entity
from textadventure.utils import CanDo


class Target:
    """
    An object that stores information on the current turn
    """
    def __init__(self, entity: Entity, team: Team):
        """

        :param entity: The entity
        :param team: The team that the entity is on
        """
        self.entity = entity
        self.team = team
        self.moves_left = 1  # one move per turn (Duh!)
        self.used_moves: List[Move] = []
        self.outcomes: Dict[Move, bool] = {}

    def set_outcome(self, move: 'Move', did_hit: bool):  # maybe change the did_hit to something other than bool later
        self.outcomes[move] = did_hit

    def did_hit(self, key: Union[Move, Entity]):
        if isinstance(key, Move):
            return self.outcomes[key]
        elif isinstance(key, Entity):
            for k, value in self.outcomes.items():
                if k.entity == key:
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

    def __init__(self, entity: Entity):
        self.entity = entity

    @abstractmethod
    def do_move(self, user: Entity, targets: List[Target]):
        pass

