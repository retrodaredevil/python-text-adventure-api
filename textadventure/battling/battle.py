from typing import List

from textadventure.battling.move import Turn
from textadventure.battling.team import Team
from textadventure.handler import Handler
from textadventure.input import InputHandler, InputHandleType, InputObject
from textadventure.player import Player, Entity


class Battle(InputHandler):
    def __init__(self, teams: List[Team]):
        self.teams = teams

        self.turns: List[Turn] = []
        self.has_started = False
        self.has_ended = False

        self.current_turn: Turn = None

    def should_update(self):
        return self.has_started and not self.has_ended

    def update(self, handler: Handler):
        """
        Assuming should_update returns True, this should be called every frame
        @param handler:
        @return
        """
        assert self.should_update(), "You shouldn't be calling update."
        assert self.current_turn is not None, "this shouldn't be None unless start hasn't been called before. (Bad)"

        if not self.current_turn.is_started:
            self.current_turn.start(self)


    def _on_end(self, handler: Handler):
        self.has_ended = True

    def start(self, handler: Handler):
        """
        Call this method when you want the battle to start.
        Calling this will add this instance to the handler's input_handlers
        @param handler:
        @return
        """
        self.has_started = True

    def get_team(self, entity: Entity):
        for team in self.teams:
            if entity in team:
                return team

        return None

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):
        team = self.get_team(player)
        if team is None:
            return None

        # here, we can assume that the player is in this battle
        def handle_function(already_handled: List[InputHandleType]) -> InputHandleType:
            if not self._should_handle_input(already_handled):
                return InputHandleType.NOT_HANDLED
