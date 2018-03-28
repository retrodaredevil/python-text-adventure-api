from typing import TypeVar, Type, Optional, TYPE_CHECKING

from textadventure.entity import Entity, Health
from textadventure.saving.playersavable import PlayerSavable
from textadventure.saving.savable import Savable
from textadventure.sending.commandsender import InputGetter, OutputSender, CommandSender
from textadventure.item.items import Wallet

if TYPE_CHECKING:
    from textadventure.handler import Handler


T = TypeVar("T")


class Player(Entity, CommandSender):
    """
    The Player class is what is used for all players. If you are using this API and would like your own player class,
    it is recommended that instead, you just use another class called something like EventsObject and store that using
    player[EventsObject] = EventsObject() (whenever you initialize your player object)
    """

    def __init__(self, input_getter: InputGetter, output: OutputSender, savable: Optional[PlayerSavable]):
        """
        :param name: The name of the player. If you would like, it can start out to be None. It is also recommended \
                    that players' names are one word while other entities are multiple so no one can name themselves\
                    the name of an important entity
        """
        super().__init__(None, Health(30, 30), None, None, savable)  # TODO max_health, current_health, location
        CommandSender.__init__(self, input_getter, output)
        self.handled_objects = []
        """A list of objects which will be saved if they inherit Savable. This list does not include self.savable as
        self.savable should help handle saving THIS list."""

        # Even though we can, we aren't going to do anything with savable right here. It is pointless since we don't
        # have an instance of Handler. We'll just trust that PlayerSavable will initialize variables if needed

    def _create_savable(self):
        return PlayerSavable()

    def __getitem__(self, item: Type[T]) -> Optional[T]:
        if not isinstance(item, type):
            raise ValueError()
        for handled_object in self.handled_objects:
            if type(handled_object) == item:
                return handled_object
        return None

    def __setitem__(self, key: Type[T], value: T):
        if not isinstance(key, type):  # if we replace type with Type, python 3.5 will be mad
            raise ValueError()

        for index, handled_object in enumerate(list(self.handled_objects)):
            if type(handled_object) == key:
                self.handled_objects[index] = value
                return

        # append the value to handled_objects if there isn't already a value for that type
        self.handled_objects.append(value)

    def get_used_name(self, sender: CommandSender):
        if sender == self:
            return "You"
        return super().get_used_name(sender)

    def update(self, handler: 'Handler') -> None:
        """
        A method called in the while True loop inside Handler
        This method will be used mostly to update the handled_objects (as of right now not needed tho)

        :param handler: The handler object
        """
        pass

    def get_wallet(self):
        for item in self.items:
            if isinstance(item, Wallet):
                return item
        return super().get_wallet()
