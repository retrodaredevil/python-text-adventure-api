from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from textadventure.item.item import Item


class Holder:  # kind of like an interface
    """
    This is a simple class that represents something that holds items
    Item picking up/dropping is handled by the weapon that is being dropped/picked up using change_holder
    """
    def __init__(self):
        self.items = []
        """Should almost never be appended to directly. You should use the item's change_holder method"""

    def can_hold(self, item: 'Item'):
        """
        Returns whether or not this holder can hold this item. Usually True and usually only reacts to the weapon type
        :param item: The item
        :return: True if it can hold the weapon False otherwise
        """
        return True

    def get_wallet(self) -> 'Holder':
        """
        This returns the holder that should be used instead of self to store money. Sometimes, this will return self but
        other times, it could return some sort of Wallet object.

        :return: The holder to be used to store money. It could be self
        """
        return self
