from typing import TypeVar, Type

from textadventure.entity import Entity, Health, Living
from textadventure.message import PlayerOutput, PlayerInput, Message, MessageType

T = TypeVar("T")


class Player(Entity):
    def __init__(self, player_input: PlayerInput, player_output: PlayerOutput, name: str):
        super().__init__(name, Health(30, 30), None)  # TODO max_health, current_health, location
        self.player_input = player_input
        self.player_output = player_output
        # self.__getitem__(PlayerFriend): Living = None
        self.handled_objects = []
        # self.__getitem__(EventsObject): 'EventsObject' = data_object

    def damage(self, damage):
        super().damage(damage)

    def __getitem__(self, item: Type[T]) -> T:
        if not isinstance(item, Type):
            raise ValueError()
        for handled_object in self.handled_objects:
            if type(handled_object) == item:
                return handled_object
        return None

    def __setitem__(self, key: Type[T], value: T):
        if not isinstance(key, Type):
            raise ValueError()

        for index, handled_object in enumerate(list(self.handled_objects)):
            if type(handled_object) == key:
                self.handled_objects[index] = value
                return
        self.handled_objects.append(value)

    def get_used_name(self, living: Living):
        if living == self:
            return "You"
        return super().get_used_name(living)

    def send_message(self, message):
        self.player_output.send_message(self.get_message(message))

    def send_wait(self, seconds):
        self.player_output.send_message(Message("", message_type=MessageType.WAIT, ending="", before="",
                                                wait_in_seconds=seconds, wait_after=False))

    def send_line(self, amount: int = 1):
        ending = Message.DEFAULT_ENDING
        if amount != 1:
            ending = ""
            for i in range(0, amount):
                ending += Message.DEFAULT_ENDING
        self.send_message(Message("", MessageType.IMMEDIATE, ending=ending))

    def clear_screen(self):
        self.send_line(100)  # do I need to use a constant variable PLTW? I do? No voy hacerlo

    def update(self, handler) -> None:
        """
        A method called in the while True loop inside Handler
        This method will be used mostly to update the handled_objects (as of right now not needed tho)
        @param handler: The handler object
        @type handler: Handler
        @return:
        """
        pass

    def take_input(self) -> str:
        """
        @return: a string or None if there is no input to take
        Once this method is called, the returned value will not be returned again (unless typed again)
        """
        return self.player_input.take_input()

    def get_wallet(self):
        """
        This method returns the Wallet item. It is here so there aren't any import errors whenever you want to use it.
        @rtype Wallet
        @return: The wallet that's in the player's items or None if there is no Wallet
        """
        from textadventure.items import Wallet
        for item in self.items:
            if isinstance(item, Wallet):
                return item
        return None
