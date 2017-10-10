from game.data import EventsObject
from textadventure.entity import *
from textadventure.player import Player
from textadventure.savable import Savable


class PlayerFriend(Living, Savable):
    def __init__(self, name):
        super().__init__(name)

    def send_message(self, message):
        raise NotImplementedError("You cannot chat with a PlayerFriend")

    def before_save(self, player, handler):
        pass

    def on_load(self, player, handler):
        pass  # nothing to update


class OtherPerson(Living):
    def __init__(self):
        super().__init__("Other Person")

    def send_message(self, message):
        raise NotImplementedError("you cannot chat with an OtherPerson")


class LauraPerson(Living):
    def __init__(self):
        super().__init__("Laura")

    def get_used_name(self, living: Living):
        if isinstance(living, Player) and not living[EventsObject].knows_laura:
            return self.__class__.UNKNOWN_LIVING_NAME
        return super().get_used_name(living)

    def send_message(self, message):
        raise NotImplementedError("You cannot chat with Laura. She doesn't like to talk.")


class NinjaDude(Living):
    """
    Ninja Dude is actually the boss but the player won't find that out until the end
    """
    def __init__(self):
        super().__init__("Ninja Dude")

    def send_message(self, message):
        raise NotImplementedError("You do not have permission to speak with the Amazing Ninja Dude. "
                                  "But really, this is an actual error.")


class NinjaEntity(SimpleHostileEntity):
    def __init__(self):
        pass
