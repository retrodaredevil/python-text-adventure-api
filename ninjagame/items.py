from enum import Enum, unique
from typing import Tuple

from textadventure.battling.weapon import Weapon
from textadventure.handler import Handler
from textadventure.items import Item
from textadventure.message import Message
from textadventure.player import Player
from textadventure.utils import MessageConstant


def create_use_message(item: Item) -> MessageConstant:
    return Message("You used {}.", named_variables=[item])


@unique
class MaterialType(Enum):
    WOOD = ("wood", 10)
    IRON = ("iron", 20)
    STEEL = ("steel", 30)
    SHINY_STEEL = ("shiny steel", 40)
    CHINESE_STEEL = ("chinese steel", 41)


@unique
class SwordType(Enum):
    # all: Tuple[str, MaterialType]
    WOODEN = ("wooden", MaterialType.WOOD)
    IRON = ("iron", MaterialType.IRON)
    STEEL = ("steel", MaterialType.STEEL)
    SHINY_STEEL = ("shiny steel", MaterialType.SHINY_STEEL)
    CHINESE_STEEL = ("chinese steel", MaterialType.CHINESE_STEEL)


class Sword(Weapon):
    def __init__(self, sword_type: SwordType):
        super().__init__("{} sword".format(sword_type.value[0]), None)  # TODO create a sword move option
        self.sword_type = sword_type

    def see(self, handler: Handler, player: Player):
        player.send_message(Message("You see a nice {}.", named_variables=[self]))

    def can_smell(self, player: Player):
        return True, "You can smell this"

    def smell(self, handler: Handler, player: Player):
        player.send_message("It smells like a sword.")

    def can_feel(self, player: Player):
        return True, "You can feel this"

    def feel(self, handler: Handler, player: Player):
        player.send_message(Message("It feels like a nice, sharp {}.", named_variables=[self]))

    def can_taste(self, player: Player):
        return True, "You can taste this."

    def taste(self, handler: Handler, player: Player):
        player.send_message("It tastes like a... Eww. don't lick your sword.")

    def can_use(self, player: Player):
        return True, "You can use this as long as you're in the right place"

    def use_item(self, handler: Handler, player: Player):
        player.send_message(create_use_message(self))
        return True

    def listen(self, handler: Handler, player: Player):
        raise NotImplementedError("Cannot listen to a sword")

