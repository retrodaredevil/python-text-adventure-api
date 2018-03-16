from typing import Tuple, Optional, Any, TYPE_CHECKING

from textadventure.item.holder import Holder
from textadventure.item.item import Item

if TYPE_CHECKING:
    from textadventure.player import Player
    from textadventure.entity import Entity
    from textadventure.handler import Handler


CoinData = Tuple[int, str]


class CoinType:
    """
    Like an enum except feel free to extend it. Each value is a CoinData
    """
    PENNY = (1, "penny")
    DIME = (10, "dime")
    QUARTER = (25, "quarter")
    DOLLAR = (100, "dollar")

    def __init__(self, worth: int, name: str):
        self.worth = worth
        self.name = name

    def create(self):
        return Coin(self)

    def __eq__(self, other):
        return isinstance(other, CoinType) and other.worth == self.worth


class Coin(Item):
    def __init__(self, coin_type):
        super().__init__(coin_type.name, True)
        self.coin_type = coin_type

    def change_holder(self, previous_holder: Optional[Holder], new_holder: Holder) -> bool:
        new_holder = new_holder.get_wallet()
        return super().change_holder(previous_holder, new_holder)

    def can_feel(self, player: 'Player'):
        return True, "You can feel this"

    def feel(self, handler: 'Handler', player: 'Player'):
        # if self.coin_type is CoinType.DOLLAR:
        #     player.send_message("You feel a nice GOLDEN coin. It's worth a lot! It's a {}!".format(name))
        player.send_message("You feel a nice coin. It's a {}!".format(self.name))

        if self in player.items:  # TODO make a more reliable way of getting the holder and how much more money there is
            holder = player
        else:
            wallet = player.get_wallet()
            assert wallet is not None
            holder = wallet

        amount_more = 0
        for item in holder.items:
            if isinstance(item, Coin) and item.coin_type == self.coin_type:
                amount_more += 1
        if holder == player:
            player.send_message("You have {} of this type of coin.".format(amount_more))
        else:
            player.send_message("There are {} of this type of coin.".format(amount_more))

    def see(self, handler: 'Handler', player: 'Player'):
        player.send_message("You see a coin. You need to feel it to tell how much it's worth")

    def can_taste(self, player: 'Player'):
        return True, "You can taste this"

    def taste(self, handler: 'Handler', player: 'Player'):
        # if self.coin_type is CoinType.DOLLAR:
        #     player.send_message("Wow, even though this tastes really bad, it's worth a lot!")
        # else:
        player.send_message("Eww, why would you want to taste this? It tastes bad!")

    def listen(self, handler: 'Handler', player: 'Player'):
        raise NotImplementedError("You can't listen to a coin")

    def can_smell(self, player: 'Player'):
        return True, "You can smell this"

    def smell(self, handler: 'Handler', player: 'Player'):
        player.send_message("It doesn't smell that great.")


class Wallet(Item, Holder):
    """
    Since we don't want the player class to have to handle coins and all that, a wallet holds and handles coins
    """

    def __init__(self):
        super().__init__("wallet", True)
        Holder.__init__(self)

    def before_save(self, source: Any, handler: 'Handler'):
        super().before_save(source, handler)
        for item in self.items:
            item.before_save(self, handler)

    def on_load(self, source: Any, handler: 'Handler'):
        super().on_load(source, handler)
        for item in self.items:
            item.on_load(self, handler)  # This wallet is the source for each coin in it

    def can_hold(self, item: Item):  # from Holder
        return isinstance(item, Coin)

    def can_take(self, entity: 'Entity'):
        return True, "You can take this"

    def can_smell(self, player: 'Player'):
        return True, "You can smell this"

    def smell(self, handler: 'Handler', player: 'Player'):
        player.send_message("Smells pretty bad.")

    def can_taste(self, player: 'Player'):
        return True, "You can taste this"

    def taste(self, handler: 'Handler', player: 'Player'):
        player.send_message("Tastes like an old wallet")

    def see(self, handler: 'Handler', player: 'Player'):
        player.send_message("It looks like an old wallet.")

    def can_feel(self, player: 'Player'):
        return True, "You can feel this"

    def feel(self, handler: 'Handler', player: 'Player'):
        player.send_message("It feels uh... Well, hmm. I still need to program this. Maybe you have a lot of money,"
                            "maybe you don't. I'm not quite sure.")

    def listen(self, handler: 'Handler', player: 'Player'):
        raise NotImplementedError("Can't listen to wallet")

