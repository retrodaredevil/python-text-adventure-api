from textadventure.command import SimpleCommandHandler
from textadventure.handler import Handler
from textadventure.input import InputObject
from textadventure.player import Player


class AttackCommandHandler(SimpleCommandHandler):
    """
    The CommandHandler that allows players to choose their attacks along with starting a battle if they aren't already \
        in a battle
    """

    command_names = ["fight", "battle", "attack", "figh", "fite", "kill", "battel", "batel", "att", "harm"]
    description = "Used to start a battle with an another entity."

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, player: Player, player_input: InputObject):
        from textadventure.battling.managing import BattleManager
        manager: BattleManager = handler.get_managers(BattleManager, 1)[0]  # get the BattleManager, there should be 1
        battles = manager.get_battles(player)
        assert len(battles) <= 1, "The player can only by in one battle"
        battle = None
        if len(battles) > 0:
            battle = battles[0]
        # now we have the battle that the player is currently in which could be None

        if battle is None:  # the player isn't in a battle
            first_arg = player_input.get_arg(0)  # remember this is a list containing the first arg at [0]
            if first_arg:  # there is a first argument
                challenged = player.location.get_referenced_entity(handler, " ".join(first_arg))



