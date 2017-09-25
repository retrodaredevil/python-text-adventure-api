from typing import List


class Holder:  # kind of like an interface
    """
    This is a simple class that represents something that holds items
    Item picking up/dropping is handled by the item that is being dropped/picked up using change_holder
    """
    def __init__(self):
        super().__init__()  # for multiple inheritance
        from textadventure.item import Item
        self.items: List['Item'] = []

    def can_hold(self, item):
        """
        Returns whether or not this holder can hold this item. Usually True and usually only reacts to the item type
        @param item: The item
        @type item: Item
        @return: True if it can hold the item False otherwise
        """
        return True
