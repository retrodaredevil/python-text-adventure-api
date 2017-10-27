import random
import typing
from abc import ABC, abstractmethod
from enum import unique, Enum, auto
from typing import List, Optional

from textadventure.battling.move import Target, Move, Turn  # needed
from textadventure.battling.team import Team
from textadventure.entity import Entity
from textadventure.utils import CanDo


if typing.TYPE_CHECKING:
    from textadventure.battling.battle import Battle


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

    def get_recommended_targets(self, turn: Turn, user: Target, teams: List[Team]) -> List[Target]:
        # importing Team could cause import errors later. Maybe not though
        r: List[Target] = []
        for team in teams:
            for entity in team.members:
                if len(r) >= self.total_number:
                    break  # we can't have more than the total number of allowed targets
                target = turn.get_target(entity)
                assert target is not None
                recommended = Targetability.RECOMMENDED  # defining a constant value to make if readable
                if (target == user and self.user == recommended) or \
                        (team == user.team and target != user and self.other_teammates == recommended) or \
                        (team != user.team and self.enemies == recommended):
                    r.append(target)

        # assert len(r) > 0, "A Move just really doesn't have any available targets huh. That's bad." or maybe its fine
        return r


class MoveOption(ABC):  # like an interface
    """
    Note, classes inheriting MoveOption should also override __str__ or it will not work properly while displaying \
        options
    """

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
        If you followed the TargetingOption returned and this returned False at [0], then this method was not created \
            correctly and you should throw an error.
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
    def get_move(self, battle: 'Battle', user: Target, turn: Turn) -> Optional[Move]:
        """
        The reason we pass user (A Target) in this method is because we only store the entity in this calss and  \
            user changes every turn
        Remember to check the user's effects to see if the user can_choose_targets that move
        @param battle:
        @param turn: The current turn
        @param user: The target that will be using the returned move. user.entity is always equal to this class's entity
        @return: The chosen move or None if no Move has been chosen yet
        """
        pass

    @abstractmethod
    def reset_option(self):
        """
        Called once the turn is over and it if this object has state that may affect the outcome of get_move, the \
            implementation of this should probably reset that.
        """
        pass


class RandomMoveChooser(MoveChooser):
    def __init__(self, entity: Entity):
        super().__init__(entity)

    @staticmethod
    def __try_choose(battle, user: Target, option: MoveOption) -> Optional[Move]:
        if not option.can_use_move(user)[0]:
            return None
        targets = option.get_targeting_option(user).get_recommended_targets(battle.current_turn, user, battle.teams)
        can_choose = option.can_choose_targets(user, targets)
        if not can_choose:
            return None
        for effect in user.effects:
            can_choose = effect.can_choose(targets, option)
            if not can_choose[0]:
                break
        if can_choose:
            return option.create_move(user, targets)
        return None

    def get_move(self, battle, user: Target, turn: Turn) -> Optional[Move]:
        options = user.get_move_options()
        assert len(options) > 0, "I wasn't prepared for this. We need to create a struggle like move."

        move: Move = None
        while move is None:  # this could be made as a recursive function but I'll keep it like this
            move = self.__try_choose(battle, user, random.choice(options))

        return move

    def reset_option(self):
        pass


class SetMoveChooser(MoveChooser):
    """
    A subclass of MoveChooser that chooses moves by allowing other parts of the code to call a method of this class \
        which sets the move option that will be used to create the Move which will be returned in get_move
    """
    def __init__(self, entity: Entity):
        super().__init__(entity)

        self.chosen_move: Optional[Move] = None

    def set_option(self, user: Target, option: MoveOption, targets: List[Target]) -> CanDo:
        """
        A method that takes a MoveOption and a list of Targets which if successful, would have created a Move which \
            will then be returned the next time get_move is called.
        This method handles the create of the Move object
        @param user: The user of the move where user.entity == self.entity
        @param option: The MoveOption that will help create the Move
        @param targets: The targets that will be targeted
        @return: A CanDo representing if the Move was successfully created. If it wasn't [0] will be False and [0] \
            is an error which should be sent to the entity
        """
        can_use = option.can_use_move(user)
        if not can_use[0]:
            return can_use

        can_target = option.can_choose_targets(user, targets)
        if not can_target[0]:
            return can_target

        for effect in user.effects:
            can_do = effect.can_choose(targets, option)  # create a new variable. if [0] is True, [1] won't be used
            if not can_do[0]:
                return can_do
        self.chosen_move = option.create_move(user, targets)
        return can_target

    def get_move(self, battle, user: Target, turn: Turn):
        return self.chosen_move

    def reset_option(self):
        self.chosen_move = None
