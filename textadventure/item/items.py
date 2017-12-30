from enum import unique, Enum
from typing import Tuple, Optional

from textadventure.handler import Handler
from textadventure.item.item import Item
from textadventure.item.holder import Holder
from textadventure.player import Player

CoinTuple = Tuple[int, str]


@unique
class CoinType(Enum):
    """
    All values in this Enum are of the type CoinTuple
    """
    PENNY = (1, "penny")
    DIME = (10, "dime")
    QUARTER = (25, "quarter")
    DOLLAR = (100, "dollar")


class Coin(Item):
    def __init__(self, coin_type: CoinType):
        super().__init__(coin_type.value[1], True)
        self.coin_type = coin_type

    def change_holder(self, previous_holder: Optional[Holder], new_holder: Holder) -> bool:
        if isinstance(new_holder, Player):
            wallet = new_holder.get_wallet()
            if wallet is not None:
                new_holder = wallet

        return super().change_holder(previous_holder, new_holder)

    def can_feel(self, player: Player):
        return True, "You can feel this"

    def feel(self, handler: Handler, player: Player):
        name = self.coin_type.value[1]
        if self.coin_type is CoinType.DOLLAR:
            player.send_message("You feel a nice GOLDEN coin. It's worth a lot! It's a {}!".format(name))
        else:
            player.send_message("You feel a nice coin. It's a {}!".format(name))
        amount_more = 0
        for item in self.holder.items:  # use self.holder because it's probably the player's wallet
            if isinstance(item, Coin) and item.coin_type is self.coin_type:
                amount_more += 1
        if self.holder == player:
            player.send_message("You have {} more of this type of coin.".format(amount_more))
        else:
            player.send_message("There are {} more of this type of coin.".format(amount_more))

    def see(self, handler: Handler, player: Player):
        player.send_message("You see a coin. You need to feel it to tell how much it's worth")

    def can_taste(self, player: Player):
        return True, "You can taste this"

    def taste(self, handler: Handler, player: Player):
        if self.coin_type is CoinType.DOLLAR:
            player.send_message("Wow, even though this tastes really bad, it's worth a lot!")
        else:
            player.send_message("Eww, why would you want to taste this? It tastes bad!")

    def listen(self, handler: Handler, player: Player):
        raise NotImplementedError("You can't listen to a coin")

    def can_smell(self, player: Player):
        return True, "You can smell this"

    def smell(self, handler: Handler, player: Player):
        player.send_message("It doesn't smell that great.")


class Wallet(Item, Holder):
    """
    Since we don't want the player class to have to handle coins and all that, a wallet holds and handles coins
    """

    def __init__(self):
        super().__init__("wallet", True)
        Holder.__init__(self)

    def before_save(self, player, handler):
        super().before_save(player, handler)
        for item in self.items:
            item.before_save(player, handler)

    def on_load(self, player, handler):
        super().on_load(player, handler)
        for item in self.items:
            item.on_load(player, handler)

    def can_hold(self, item: Item):  # from Holder
        return isinstance(item, Coin)

    def can_take(self, player: Player):
        return True, "You can take this"

    def can_smell(self, player: Player):
        return True, "You can smell this"

    def smell(self, handler: Handler, player: Player):
        player.send_message("Smells pretty bad.")

    def can_taste(self, player: Player):
        return True, "You can taste this"

    def taste(self, handler: Handler, player: Player):
        player.send_message("Tastes like an old wallet")

    def see(self, handler: Handler, player: Player):
        player.send_message("It looks like an old wallet.")

    def can_feel(self, player: Player):
        return True, "You can feel this"

    def feel(self, handler: Handler, player: Player):
        player.send_message("It feels uh... Well, hmm. I still need to program this. Maybe you have a lot of money,"
                            "maybe you don't. I'm not quite sure.")

    def listen(self, handler: Handler, player: Player):
        raise NotImplementedError("Can't listen to wallet")

