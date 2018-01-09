from typing import Callable, Tuple, TYPE_CHECKING

from textadventure.saving.savable import Savable

if TYPE_CHECKING:
    from textadventure.handler import Handler
    from textadventure.entity import Identifiable


class HandlerInitialize:
    def __init__(self, key, init_callable: Callable[['Handler'], Savable]):
        """

        :param key: The key the Savable should be saved under or is already saved under in handler.savables
        :param init_callable: Will be called only if there wasn't a Savable found under key 'key' in handler.savables.
                This should return the Savable that will be saved under 'key'.
        """
        self.key = key
        self.init_callable = init_callable

    def do_init(self, handler: 'Handler'):
        savable = handler.get_savable(self.key)
        if savable is None:
            savable = self.init_callable(handler)
            handler.set_savable(self.key, savable)


class IdentifiableInitialize(HandlerInitialize):
    def __init__(self, key, create_callable: Callable[[], Tuple['Identifiable', Savable]]):
        """
        :param key: The key to get the Savable from Handler if it is there
        :param create_callable: A Callable that will be called only if a Savable wasn't found in Handler. This should\
                return the Identifiable that will be added to handler.identifiables and also return the savable that\
                will be put under the key. (It returns a Tuple value)
        """
        def init_callable(handler: 'Handler'):
            created, savable = self.create_callable()
            handler.identifiables.append(created)
            # don't call handler.set_savable because the superclass does that
            return savable

        super().__init__(key, init_callable)
        self.create_callable = create_callable

