import random
from abc import ABC, abstractmethod
from typing import List, Optional

from textadventure.battling.move import Target, Move, Turn
from textadventure.entity import Entity
from textadventure.utils import CanDo


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
        Similar to can_use_move, however, this is specifically for reporting if the user can target the targets
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
    def get_move(self, turn: Turn, user: Target) -> Optional[Move]:
        """
        @param turn: The current turn
        @param user: The target that will be using the returned move. user.entity is always equal to this class's entity
        @return: The chosen move or None if no Move has been chosen yet
        """
        pass


class RandomMoveChooser(MoveChooser):
    def __init__(self, entity: Entity):
        super().__init__(entity)

    def get_targets(self, turn: Turn, option: MoveOption) -> List[Target]:
        # TODO
        pass

    def try_choose(self, turn: Turn, user: Target, option: MoveOption) -> Optional[Move]:
        if not option.can_use_move(user):
            return None
        targets = self.get_targets(turn, option)
        if option.can_choose(user, targets):
            return option.create_move(user, targets)
        return None

    def get_move(self, turn: Turn, user: Target) -> Optional[Move]:
        options = user.get_move_options()
        assert len(options) > 0, "I wasn't prepared for this. We need to create a struggle like move."

        move: Move = None
        while move is None:  # this could be made as a recursive function but I'll keep it like this
            move = self.try_choose(turn, user, random.choice(options))

        return move
