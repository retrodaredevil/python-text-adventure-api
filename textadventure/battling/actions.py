import typing

from textadventure.action import Action

if typing.TYPE_CHECKING:
    from textadventure.battling.battle import Battle


"""
A file dedicated to define implementations of the Action class related to the battling api
"""


class BattleEnd(Action):
    """
    An Action that may have unexpected results when cancelling. Basically an event that tells you when the Battle ends.
    """
    def __init__(self, battle: 'Battle'):
        super().__init__()
        self.battle: 'Battle' = battle

    def _do_action(self, handler):
        self.battle.has_ended = True

