from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from textadventure.utils import CanDo


if TYPE_CHECKING:
    from textadventure.handler import Handler


class Action(ABC):
    """
    A base class for for all actions that should be inherited by all actions
    As of right now, this class has no use except for using it to help with typing and isinstance stuff.
    """

    def __init__(self):
        super().__init__()
        self.can_do = (True, "By default this is true")

    @abstractmethod
    def _do_action(self, handler: 'Handler') -> CanDo:
        """
        When overridden, this method should do whatever is wanted to matter what the state of the object is
        (Don't use the can_do field to alter what happens in this method)
        Usually, self.can_do should be returned.

        :param handler: The handler object
        :return whether or not the action was done (Return self.can_do or if you need to change it, change it)
        """
        pass

    def try_action(self, handler: 'Handler') -> CanDo:
        """
        Should be called after calling handlers do_action. This will make sure that if this Action was cancelled, it\
        won't be called (So you don't have to check can_do manually

        :param handler: The handler object to be passed to _do_action
        :return: Whether or not the action was successful
        """
        if self.can_do[0]:
            return self._do_action(handler)
        return self.can_do
        # do nothing with else because we don't have a player to send it to right now
