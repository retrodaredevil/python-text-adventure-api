from typing import List, Optional

from textadventure.battling.actions import EntityChallengeAction
from textadventure.battling.choosing import SetMoveChooser, MoveOption
from textadventure.battling.managing import BattleManager
from textadventure.battling.move import Target
from textadventure.commands.command import SimpleCommandHandler
from textadventure.handler import Handler
from textadventure.input.inputhandling import InputObject, InputHandleType
from textadventure.message import Message
from textadventure.player import Player
from textadventure.utils import join_list


class AttackCommandHandler(SimpleCommandHandler):
    """
    The CommandHandler that allows players to choose their attacks along with starting a battle if they aren't already \
        in a battle
    """

    command_names = ["fight", "battle", "attack", "figh", "fite", "kill", "battel", "batel", "att", "harm"]
    description = "Used to start a battle with an another entity."

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: Handler, player: Player, player_input: InputObject) -> InputHandleType:
        # from textadventure.battling.managing import BattleManager importing non-locally now
        manager = handler.get_managers(BattleManager, 1)[0]  # get the BattleManager, there should be 1
        battles = manager.get_battles(player)
        assert len(battles) <= 1, "The player can only by in one battle"
        battle = None
        if len(battles) > 0:
            battle = battles[0]
        # now we have the battle that the player is currently in which could be None

        if battle is None:  # the player isn't in a battle
            first_arg = player_input.get_arg(0, False)  # remember this is a list containing the first arg at [0]
            # ignore_unimportant_before is False (^)because we want to get everything the player typed after the command

            if not first_arg:  # there isn't a first argument
                player.send_message("Who would you like to battle?")
                return InputHandleType.HANDLED
            reference = " ".join(first_arg)
            challenged = player.location.get_referenced_entity(handler, reference)
            if challenged is None:
                player.send_message(Message("Cannot find entity named: '{}' in your current location.",
                                            named_variables=[reference]))
                return InputHandleType.HANDLED
            challenge_action = EntityChallengeAction(player, challenged)
            handler.do_action(challenge_action)
            challenge_action.try_action(handler)
            return InputHandleType.HANDLED

        # now we know the player is in a battle since Battle isn't None
        assert not battle.has_ended, "For whatever reason, we received at battle that was ended."
        if not battle.has_started:
            player.send_message("Sorry, for whatever reason the battle hasn't started yet. This could be an error.")
            return InputHandleType.HANDLED
        turn = battle.current_turn
        assert turn is not None, "The battle is started and there's no current_turn ??? That would be an error."
        user = turn.get_target(player)
        assert isinstance(user.move_chooser, SetMoveChooser), "We need the player's MoveChooser to be a SetMoveChooser."

        first_arg = player_input.get_arg(0)
        if not first_arg:
            return self.__class__.send_options(player, user)
        try:
            number = int(first_arg[0])
            # now that we know the first argument is a number, the player wants to choose a move
            return self.__class__.choose_option_from_number(battle, number, player, user)
        except ValueError:
            pass  # the first argument was not a number so lets test for something else now
        if first_arg[0].lower() == "members":
            return self.__class__.send_members(battle, player)

        self.send_help(player)
        return InputHandleType.HANDLED

    @staticmethod
    def send_options(player, user):
        options = user.get_move_options()
        rep = join_list([str(option) for option in options], use_brackets=True, use_indexes=True)
        player.send_message(Message("Options: {}".format(rep), named_variables=options))
        chooser = user.move_chooser  # should be a SetMoveChooser
        if chooser.chosen_move is not None:
            player.send_message(Message("You have already chosen: {}", named_variables=[chooser.chosen_move]))
        return InputHandleType.HANDLED

    @staticmethod
    def choose_option_from_number(battle, number, player, user, chosen_targets: Optional[List[Target]] = None):
        options = user.get_move_options()
        length = len(options)
        if number < 0 or number >= length:
            player.send_message(Message("The number {} is not valid", named_variables=[number]))
            return InputHandleType.HANDLED
        option = options[number]  # a MoveOption
        chooser = user.move_chooser  # A SetMoveChooser

        if chosen_targets is None:  # lets automatically create the list for the player.
            chosen_targets = option.get_targeting_option(user).get_recommended_targets(battle.current_turn, user,
                                                                                       battle.teams)

        was_successful = chooser.set_option(user, option, chosen_targets)
        if not was_successful[0]:
            player.send_message(was_successful[1])
        return InputHandleType.HANDLED

    @staticmethod
    def send_members(battle, player):
        for index, team in enumerate(battle.teams):
            player.send_message(Message("{}: {}".format(index, "{}"), named_variables=team))

        return InputHandleType.HANDLED
