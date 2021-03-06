from typing import List, Optional

from textadventure.battling.move import Turn, Target
from textadventure.battling.team import Team
from textadventure.handler import Handler
from textadventure.player import Player, Entity
from textadventure.sending.message import Message
from textadventure.utils import MessageConstant


class Battle:
    """
    A class that is used to simulate a turn based battle. The uniqueness of the battle is up to custom effects,\
    managers, and weapons.
    """
    def __init__(self, teams: List[Team]):
        self.teams = teams

        # self.turns: List[Turn] = []  # commented because nowhere in the code is this list appended to
        self.has_started = False
        self.has_ended = False

        self.current_turn = None

    def is_going_on(self):
        """
        :return: True if the battle has started, and it hasn't ended yet
        """
        return self.has_started and not self.has_ended

    def should_update(self) -> bool:
        """
        Just makes sure that the battle has started and makes sure that the battle isn't over so you don't update\
            when you shouldn't
        :return: True if you should call the update method, False otherwise
        """
        return self.is_going_on()

    def update(self, handler: Handler):  # not overridden - handled by a BattleManager
        """
        Assuming should_update returns True, this should be called every frame
        :param handler: The handler object
        """
        assert self.should_update(), "You shouldn't be calling update."
        assert self.current_turn is not None, "this shouldn't be None unless start hasn't been called before. (Bad)"

        if not self.current_turn.is_started:
            self.current_turn.start(self)

        self.current_turn.update(self, handler)

        if self.current_turn.is_done:
            if self.__is_done():
                self.has_ended = True
                from textadventure.battling.actions import BattleEnd
                end_action = BattleEnd(self, self.get_alive_teams()[0])  # TODO make a safer way to get winning team
                handler.do_action(end_action)
                assert end_action.can_do[0], "We aren't prepared for this. Why would you cancel it?"
                end_action.try_action(handler)  # calling this will display results
                return
            self.current_turn = self.__next_turn(self.current_turn)

    def __next_turn(self, last_turn: Optional[Turn]) -> Turn:
        number = 0
        targets = []
        if last_turn is not None:
            number = last_turn.number + 1

            for target in last_turn.targets:
                targets.append(target.create_target_next_turn(last_turn, number))
        else:  # lets create some default values (mostly for targets)
            from textadventure.battling.choosing import RandomMoveChooser, SetMoveChooser
            for team in self.teams:
                for entity in team.members:
                    if isinstance(entity, Player):
                        chooser = SetMoveChooser(entity)
                    else:
                        chooser = RandomMoveChooser(entity)
                    targets.append(Target(entity, team, chooser, number))

        return Turn(number, targets)

    def __is_done(self):
        number_alive = 0
        for team in self.teams:
            if not team.is_dead():
                number_alive += 1

        return number_alive <= 1

    def broadcast_healths(self):
        for team in self.teams:
            for entity in team.members:
                self.broadcast(Message("{}'s hp: {}", named_variables=[entity, entity.health]))

    def start(self, handler: Handler):
        """
        Call this method when you want the battle to start.
        Calling this will add this instance to the handler's input_handlers
        :param handler: The Handler object
        """
        from textadventure.battling.actions import BattleStart
        self.current_turn = self.__next_turn(None)  # set current_turn so not None when a manager handles the action
        battle_start = BattleStart(self)  # probably uses current_turn to add effects to the entities/targets
        handler.do_action(battle_start)
        battle_start.try_action(handler)
        # battle_start will set self.has_started to True

    def get_team(self, entity: Entity) -> Optional[Team]:
        """
        Used to get the team of the passed entity. Can also be used to check if the entity is in the battle \
            (Compare returned team to None
        :param entity: The entity that you are getting the team of
        :return: The team that the entity is on or None if the entity is on None of the teams (Not in the battle)
        """
        for team in self.teams:
            if entity in team:
                return team

        return None

    def get_alive_teams(self) -> List[Team]:
        r = []

        for team in self.teams:
            if not team.is_dead():
                r.append(team)

        return r

    def broadcast(self, message: MessageConstant):
        if message is None:
            return
        for team in self.teams:
            for target in team.members:
                target.send_message(message)

    # def on_input(self, handler: Handler, player: Player, input_getter: InputObject):
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
