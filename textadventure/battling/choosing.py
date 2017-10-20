import random
from abc import ABC, abstractmethod
from enum import unique, Enum, auto
from typing import List, Optional

from textadventure.battling.move import Target, Move, Turn
from textadventure.entity import Entity
from textadventure.utils import CanDo


@unique
class Targetability(Enum):  # this is now one word. Deal with it. I think it describes the class pretty well, though
    RECOMMENDED = auto()
    NOT_RECOMMENDED = auto()
    NOT_ABLE = auto()


class TargetingOption:
    """
    Represents what you can, should and can't select as targets
    """
    def __init__(self, user: Targetability, other_teammate: Targetability, enemies: Targetability,
                 total_number: Optional[int]):
        """
        Creates a TargetingOption representing what you can, should and can't select as targets
        @param user: Can you target yourself?
        @param other_teammate: Can you target other people on your team
        @param enemies: Can you target your enemies?
        @param total_number: What are the total number of targets you can target. Use None to represent infinite
        """
        self.user = user
        self.other_teammates = other_teammate
        self.enemies = enemies
        self.total_number = total_number


class MoveOption(ABC):  # like an interface

    @abstractmethod
    def can_use_move(self, user: Target) -> CanDo:
        """

        @param user: The user that will end up using this Move
        @return: A CanDo tuple where [0] is a boolean value that determines whether or not you can use this move
        """
        pass

    @abstractmethod
    def get_targeting_option(self, user: Target) -> TargetingOption:
        """
        Returns a TargetingOption that usually isn't user specific and is type specific (what type of class this is) \
            But it could be user specific if you wanted it to be.
        @param user: The user that will use this move along with choosing a set of targets based on
        @return: The TargetingOption that is used for this move and can be changed for a specific user
        """
        pass

    @abstractmethod
    def can_choose_targets(self, user: Target, targets: List[Target]) -> CanDo:
        """
        Similar to can_use_move, however, this is specifically for reporting if the user can target the targets
        If you followed the TargetingOption returned and this returned False at [0], then throw an exception please.\
            please do that. Like really, do that.
        Note that if you are handling a player's input and the player's input wants to select targets that don't\
            follow the TargetingOption returned, you SHOULD call this method so you can send \
            them the error message at [1]
        @param user: The user that will end up using this Move
        @param targets: The list of targets that the player is trying to target
        @return: A CanDo tuple where [0] is a boolean value that determines whether or not the user can target targets
        """
        pass

    @abstractmethod
    def create_move(self, user: Target, targets: List[Target]) -> Move:
        """
        A method that creates a move the the user as the user and targets as the targets
        @param user: The person using the move and what should be in the returned Move's user field
        @param targets: The targets that will be targeted and should be in the returned Move's targets field
        @return: A move that is different for each MoveOption
        """
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
        The reason we pass user (A Target) in this method is because we only store the entity in this calss and  \
            user changes every turn
        Remember to check the user's effects to see if the user can_choose_targets that move
        @param turn: The current turn
        @param user: The target that will be using the returned move. user.entity is always equal to this class's entity
        @return: The chosen move or None if no Move has been chosen yet
        """
        pass


class RandomMoveChooser(MoveChooser):
    def __init__(self, entity: Entity):
        super().__init__(entity)

    def __get_targets(self, turn: Turn, option: MoveOption) -> List[Target]:
        # TODO
        pass

    def __try_choose(self, turn: Turn, user: Target, option: MoveOption) -> Optional[Move]:
        if not option.can_use_move(user):
            return None
        targets = self.__get_targets(turn, option)
        can_choose = option.can_choose_targets(user, targets)
        if not can_choose:
            return None
        for effect in user.effects:
            can_choose = effect.can_choose_targets(targets, option)
        if can_choose:
            return option.create_move(user, targets)
        return None

    def get_move(self, turn: Turn, user: Target) -> Optional[Move]:
        options = user.get_move_options()
        assert len(options) > 0, "I wasn't prepared for this. We need to create a struggle like move."

        move: Move = None
        while move is None:  # this could be made as a recursive function but I'll keep it like this
            move = self.__try_choose(turn, user, random.choice(options))

        return move
