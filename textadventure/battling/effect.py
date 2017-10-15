from abc import ABC, abstractmethod
from typing import List

from textadventure.battling.choosing import MoveOption
from textadventure.battling.move import Move, Target, Turn
from textadventure.utils import CanDo


"""
Make sure this isn't imported at the top of any files in this package because it will cause import errors.
"""


class Effect(ABC):
    """
    Note that the methods are defined in the order that they are called. Their documentation should say that too.

    """
    # TODO add a method that helps with forcefully removing an effect (A way for recovery moves to remove effects)

    CAN_CHOOSE: CanDo = (True, "This effect does not affect the options you are allowed to choose")
    CAN_MOVE: CanDo = (True, "This effect does not affect the outcome of at attack")

    def __init__(self, user: Target):
        self.user = user

    @abstractmethod
    def can_choose(self, targets: List[Target], option: MoveOption) -> CanDo:
        """
        Called first because it's called before the Move object is created
        Should be used to test for things like if you can choose a certain type of move, if you can target so many\
            people. Should not call any of option's can_use methods because that will already be handled for you
        @param targets: The targets the user is trying to target
        @param option: The move option requested by the user
        @return: Whether or not the user can use the selected move
        """
        pass

    @abstractmethod
    def can_move(self, move: Move) -> CanDo:
        """
        Basically says if the move has been missed or not. Maybe there's an affect that makes each move have a %50\
            chance of hitting it. An this method could run a test to see if the move should hit.
        If it returns false, the player will not be able to choose a different move because this one failed. And\
            move.do_move will NOT be called
        Could be renamed to will_move_be_success if you want to think about it like that
        @param move: The move that is about to be used. It contains the user and the targets
        @return: whether or not the move should be performed. If [0] is false, the move will fail and [1] will be \
                    broadcasted
        """
        pass

    @abstractmethod
    def before_turn(self, turn: Turn, move: Move):
        """
        Called after can_move and can_choose before the all of the moves have happened
        @param turn: the turn that is ongoing
        @param move: The move that is about to be performed
        @return: None
        """
        pass

    @abstractmethod
    def after_move(self, turn: Turn, move: Move):
        """
        Called right after the move has happened.
        @param turn: The turn that will soon finish after every other Target performs their move
        @param move: The move that was just performed by the user
        @return: None
        """
        pass

    @abstractmethod
    def after_turn(self, turn: Turn, move: Move):
        """
        Called after all the moves have happened
        The main method that should be where the main code to do something/affect the user
        @param turn: The turn that is about to be over
        @param move: The move that the user performed
        @return: None
        """
        pass

    @abstractmethod
    def should_stay(self, previous_turn: Turn) -> bool:
        """
        Is used to tell whether or not the effect should move on to the next turn
        The next turn is about to be created, we just need to know if this effect should stay with the user
        @param previous_turn: The turn that has just finished.
        @return: True if the effect should stay on the user, False if the effect should be removed
        """
        pass
