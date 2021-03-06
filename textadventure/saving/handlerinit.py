from typing import Callable, TYPE_CHECKING, Optional, Any, Tuple

from textadventure.entity import Identifiable
from textadventure.saving.savable import Savable, HasSavable

if TYPE_CHECKING:
    from textadventure.handler import Handler


class HandlerInitialize:
    def __init__(self, key, init_callable: Callable[['Handler'], Tuple[Savable, Any]]):
        """

        :param key: The key the Savable should be saved under or is already saved in the handler savables dict
        :param init_callable: Will be called only if there wasn't a Savable found under key 'key' in handler.savables.
                This should return the Savable that will be saved under 'key'.
        """
        self.key = key
        self.init_callable = init_callable

    def do_init(self, handler: 'Handler'):
        savable, source = self.init_callable(handler)
        handler.set_savable(self.key, savable, source)


class IdentifiableInitialize(HandlerInitialize):
    def __init__(self, key, create_callable: Callable[[Optional[Savable]], HasSavable]):
        """
        :param key: The key to get the Savable from Handler if it is there
        :param create_callable: A Callable that will be called only if a Savable wasn't found in Handler. This should\
                return the Identifiable that will be added to handler.identifiables which is also an instance of
                HasSavable
        """
        def init_callable(handler: 'Handler'):
            value = handler.get_savable(key)
            savable, source = value if value is not None else (None, None)

            created = self.create_callable(savable)
            assert isinstance(created, Identifiable) and isinstance(created, HasSavable)
            if savable is not None:  # if there was saved data, load it
                savable.on_load(created, handler)

            handler.identifiables.append(created)
            # don't call handler.set_savable because the superclass does that
            return created.savable, created  # may be different than savable

        super().__init__(key, init_callable)
        self.create_callable = create_callable

