from typing import List

from textadventure.customgame import CustomGame
from textadventure.handler import Handler
from textadventure.player import Player


class Main:
    """
    Used to initialize a CustomGame object along with constructing a Handler object making initializing a game\
    a lot simpler and more abstract
    """
    def __init__(self, game: CustomGame):
        """
        """
        self.game = game

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
        A method that is used for each player that joins no matter if they are new or not and no matter when they join.

        Note that this should NOT be overridden. Since this calls self.on_player_start. You can change that when\
        creating this object

        :param player: The player that has just joined
        """
        # TODO make another method that makes sure all of the player's data is loaded if the player isn't new
        self.game.new_player(player)

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
