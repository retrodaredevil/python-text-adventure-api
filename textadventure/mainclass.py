from typing import List, Callable

from textadventure.handler import Handler
from textadventure.player import Player


class Main:
    """
    A Main class to help with the initiation of a game. Note that subclasses aren't meant to be used to customize\
    the game. Instead, they should be used to change what players start in the game, how a player is sent messages.
    """
    def __init__(self, on_player_start: Callable[[Handler, Player], None],
                 on_player_end: Callable[[Handler, Player], None]):
        """
        :param on_player_start: A function that is passed a Handler and a Player that should be customized by the\
                game being played to make sure each player ends up in the correct spot when they first start the game
        """
        self.on_player_start = on_player_start
        self.on_player_end = on_player_end

        self.handler = None
        """Member that is initialized when start is called"""

    def create_players(self) -> List[Player]:
        """
        The method that is called on the start of a game and normally where you add players that are ready to play\
        the game right away. (Usually client side)

        The default implementation returns an empty list

        When this method is called, self.handler will not be None

        :return: A list of players to add immediately
        """
        return []

    def init_player(self, player: Player):
        """
        A method that is used for each player that joins no matter if they are new or not.

        Note that this should NOT be overridden. Since this calls self.on_player_start. You can change that when\
        creating this object

        :param player: The player that has just joined
        """
        # TODO make another method that makes sure all of the player's data is loaded if the player isn't new
        self.on_player_start(self.handler, player)

    def start(self):
        assert self.handler is None, "If self.handler isn't None, then start must have been called before this."
        self.handler = Handler()

        players = self.create_players()
        for player in players:
            self.init_player(player)

    def end(self):
        """
        Method that should not be overridden. It will call on_end
        """
        self.on_end()

    def on_end(self):
        """
        Method that is called by end(). This should be overridden.
        """
        pass
        # TODO replace this with on_player_end idk



