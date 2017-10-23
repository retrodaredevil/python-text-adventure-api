from typing import List, Optional

from textadventure.battling.move import Turn
from textadventure.battling.team import Team
from textadventure.handler import Handler
from textadventure.input import InputHandler, InputHandleType, InputObject, InputHandle
from textadventure.player import Player, Entity
from textadventure.utils import MessageConstant


class Battle:
    def __init__(self, teams: List[Team]):
        self.teams = teams

        self.turns: List[Turn] = []
        self.has_started = False
        self.has_ended = False

        self.current_turn: Turn = None

    def is_going_on(self):
        """
        @return: True if the battle has started, and it hasn't ended yet
        """
        return self.has_started and not self.has_ended

    def should_update(self) -> bool:
        """
        Just makes sure that the battle has started and makes sure that the battle isn't over so you don't update\
            when you shouldn't
        @return: True if you should call the update method, False otherwise
        """
        return self.is_going_on()

    def update(self, handler: Handler):  # not overridden - handled by a BattleManager
        """
        Assuming should_update returns True, this should be called every frame
        @param handler:
        @return
        """
        assert self.should_update(), "You shouldn't be calling update."
        assert self.current_turn is not None, "this shouldn't be None unless start hasn't been called before. (Bad)"

        if not self.current_turn.is_started:
            self.current_turn.start(self)

        self.current_turn.update(self)

    def start(self, handler: Handler):
        """
        Call this method when you want the battle to start.
        Calling this will add this instance to the handler's input_handlers
        @param handler: The Handler object
        """
        self.has_started = True

    def get_team(self, entity: Entity) -> Optional[Team]:
        """
        Used to get the team of the passed entity. Can also be used to check if the entity is in the battle \
            (Compare returned team to None
        @param entity: The entity that you are getting the team of
        @return: The team that the entity is on or None if the entity is on None of the teams (Not in the battle)
        """
        for team in self.teams:
            if entity in team:
                return team

        return None

    def broadcast(self, message: MessageConstant):
        if message is None:
            return
        for team in self.teams:
            for target in team.members:
                target.send_message(message)

    # def on_input(self, handler: Handler, player: Player, player_input: InputObject):
    #     commented cuz not an input handler
    #     team = self.get_team(player)
    #     if team is None:
    #         return None
    #
    #     # here, we can assume that the player is in this battle
    #     def handle_function(already_handled: List[InputHandleType]) -> InputHandleType:
    #         if not self._should_handle_input(already_handled):
    #             return InputHandleType.NOT_HANDLED
    #
    #         return InputHandleType.HANDLED
    #
    #     return InputHandle(7, handle_function, self)
