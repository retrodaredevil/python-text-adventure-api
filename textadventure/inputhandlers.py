from typing import List

from textadventure.handler import Handler
from textadventure.input import InputHandler, InputObject, InputHandleType, InputHandle
from textadventure.message import StreamOutput, Message, MessageType
from textadventure.player import Player


class SettingsHandler(InputHandler):
    def __init__(self, allowed_player: Player):
        """
        :param allowed_player: The only player that this will react to
        """
        self.allowed_player = allowed_player

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):

        if player != self.allowed_player or player_input.get_command().lower() != "setting" \
                or type(player.player_output) is not StreamOutput:
            return None

        output = player.player_output

        def handle_function(already_handled: List[InputHandleType]) -> InputHandleType:
            if len(player_input.get_arg(1)) != 0:
                if player_input.get_arg(0)[0].lower() == "speed":
                    speed = player_input.get_arg(1)[0].lower()
                    if speed == "fast":
                        output.wait_multiplier = 0.4
                        player.send_message("Set speed to fast.")
                        return InputHandleType.HANDLED_AND_DONE
                    elif speed == "normal":
                        output.wait_multiplier = 1
                        player.send_message("Set speed to normal")
                        return InputHandleType.HANDLED_AND_DONE
                    else:
                        pass  # flow down to send help message

            player.send_message(Message("Help for setting command: \n"
                                        "\tspeed: setting speed <fast:normal>", MessageType.IMMEDIATE))
            return InputHandleType.HANDLED_AND_DONE

        return InputHandle(0, handle_function, self)
