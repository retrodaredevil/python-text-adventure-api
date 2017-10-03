from abc import ABC, abstractmethod
from typing import List, Dict, Union

from textadventure.battling.team import Team
from textadventure.entity import Entity


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

        self.is_done = False
        self.is_started = True  # by default, whenever creating a Turn, we will be on that turn


class Move(ABC):
    def __init__(self, user: Target):
        self.user = user

    @abstractmethod
    def do_move(self, turn: Turn, user: Entity, targets: List[Target]):
        pass


def main():
    print("test")  # used to make sure that there are no "not defined" errors with the types


if __name__ == '__main__':
    main()
