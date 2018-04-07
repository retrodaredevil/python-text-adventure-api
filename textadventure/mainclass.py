import time
from pathlib import Path
from typing import List

from textadventure.customgame import CustomGame
from textadventure.handler import Handler, HandlerSavable, PlayerHandler
from textadventure.manager import Manager
from textadventure.player import Player
from textadventure.saving.saving import SavePath, load_data


class Main:
    """
    Used to initialize a CustomGame object along with constructing a Handler object making initializing a game\
    a lot simpler and more abstract
    """
    def __init__(self, game: CustomGame, custom_managers: List[Manager], save_path: SavePath, rest=0.0, clean=False,
                 player_handler: PlayerHandler = None):
        """
        Note: Custom managers do not yet call on_action when an action happens. This may be easily implemented in the
        future but, is not needed as of right now

        :param game: The custom game that this helps initialize
        :param custom_managers: List of managers that will be updated before handler. Note these managers should NOT
                                be related to the game and should not alter game play at all. They should only be
                                cosmetic or should help with things unrelated to the game
        :param rest: The amount of time to wait between each update. If this is not 0, calling update will pause the
                     program
        :param clean: True if the program shouldn't attempt to load any data which will overwrite existing data when
                      saving
        """
        self.game = game

        self.handler = None
        """Member that is initialized when start is called"""
        self.custom_managers = custom_managers
        self.save_path = save_path if save_path is not None else SavePath(Path("./save.dat.d"))
        self.rest = rest
        self.clean = clean
        self.player_handler = player_handler

    def create_players(self) -> List[Player]:
        """
        The method that is called on the start of a game and normally where you add players that are ready to play\
        the game right away. (Usually client side)

        The default implementation returns an empty list

        When this method is called, self.handler will not be None

        Note: When overriding this is not meant to return a list of subclasses of Player. It should only be used to
        create players that will start in the game. (Normally there should be just one) (If this Main instance controls
        a server, then the list would probably be empty)

        :return: A list of players to add immediately
        """
        return []

    def init_player(self, player: Player):
        """
        A method that is used for each player that joins no matter if they are new or not and no matter when they join.

        Note that this should NOT be overridden. Since this calls self.on_player_start. You can change that when
        creating this object

        Note that self.handler may be null and player.location may be null. This method should not try to set location

        :param player: The player that has just joined
        """
        if player.is_new:
            self.game.new_player(player)

    def start(self):
        assert self.handler is None, "If self.handler isn't None, then start must have been called before this."

        players = self.create_players()
        for player in players:
            self.init_player(player)

        locations = self.game.create_locations()

        input_handlers = list(self.game.create_custom_input_handlers())
        input_handlers.extend(self.game.create_input_handlers())

        managers = list(self.game.create_custom_managers())
        managers.extend(self.game.create_managers())

        message = "Unable to load data."
        savable = None
        data = load_data(self.save_path.get_handler_path())
        if not isinstance(data, str):
            if isinstance(data, HandlerSavable):
                savable = data
                message = "Loaded data successfully."
            else:
                message = "Tried to load data for handler and got: {}".format(data)
        self.handler = Handler(list(players), locations, input_handlers, managers, self.save_path, savable,
                               player_handler=self.player_handler)
        self.handler.broadcast(message)

        self.game.add_other(self.handler)

        self.handler.start()
        for player in self.handler.get_players():
            if player.is_new:
                player.location = self.game.get_starting_location(self.handler, player)
            else:
                player.savable.on_load(player, self.handler)

            player.location.on_enter(player, None, self.handler)

    def update(self):
        self.handler.update()
        for manager in self.custom_managers:
            manager.update(self.handler)

        time.sleep(self.rest)

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


class ClientSideMain(Main):
    def __init__(self, game: CustomGame, custom_managers: List[Manager], player: Player, save_path: SavePath, rest=0.0,
                 clean=False, player_handler: PlayerHandler = None):
        super().__init__(game, custom_managers, save_path, rest=rest, clean=clean, player_handler=player_handler)
        self.player = player

    def create_players(self):
        return [self.player]
