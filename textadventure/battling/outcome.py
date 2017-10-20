from typing import List

from textadventure.utils import CanDo


class OutcomePart:
    def __init__(self):
        pass


class MoveOutcome:

    def __init__(self, can_move: CanDo, was_successful: CanDo):
        """

        @param can_move: A CanDo tuple representing if the player was able to try to perform the move. This can be \
                         cancelled by effects.
        @param was_successful:
        """
        self.can_move: CanDo = can_move
        self.was_successful: CanDo = was_successful

        self.parts: List[OutcomePart] = []

