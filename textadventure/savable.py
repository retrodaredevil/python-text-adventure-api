from abc import ABC, abstractmethod
from typing import List

"""
To avoid namespace and type error, this file shouldn't import anything from the textadventure package
"""

is_saving = False


class Savable(ABC):
    """
    A class that, if implemented, will allow you to save this class. Note that just implementing this class does\
        nothing. You must have another object/part of code that handles saving this. For this reason, if you want to\
        save all the data in your class at one point in your code, you can implement this class. Beware, if this object\
        gets into a wrong list, it could be saved.
    If you don't want to save all of the data in the class, it is recommended to store the object that you want to be\
        saved as a field making that a Savable, however, that object will usually have to make it into a list\
        of an object that handles it, or the class storing the Savable will have to make sure that somewhere in\
        the code it saves it.

    Now that you've read all that, basically it says: "Implementing this doesn't automatically make this save and\
        if this is stored somewhere, there might be side effects from implementing this"
    Data in each instance/implementation should be player specific TODO edit comment

    If you are getting a KeyError, remember to override __new__ and set any fields that are in the non_serialized list.
    """

    def __init__(self):
        super().__init__()  # for multiple inheritance
        self.non_serialized: List[str] = []
        """Appending to this list allows you to stop pickler from saving a field"""

    # def __getattribute__(self, item):  # this is funny. I tried getting it to work with pickle. Don't try this
    #     # print("requested {} from type: {}".format(item, type(self)))
    #     if is_saving and item != "non_serialized" \
    #             and item in self.non_serialized:  # if this throws an error. init hasn't been called
    #         print("ignored: " + item)
    #         return None
    #     return super().__getattribute__(item)

    def __getstate__(self):
        # thanks https://stackoverflow.com/questions/6313421/can-i-mark-variables-as-transient-so-they-wont-be-pickled
        state = dict(self.__dict__)
        for item in self.non_serialized:
            del state[item]

        return state

    @abstractmethod
    def before_save(self, player, handler):
        """
        Called before the data will be saved. Override to do whatever you want with it.
        @param player: The player whose data will be saved
        @type player: Player
        @param handler: The handler object
        @type handler: Handler

        # @return: [0] is True if you can save, [0] is False if you can't and [1] will be the reason why
        @return: None
        """
        pass

    @abstractmethod
    def on_load(self, player, handler):
        """
        Called when the object is loaded into the player's handled_object
        this should not be called from __init__ and should and will only be called when unserializing/unpickling data\
            (that's handled for you)
        @param player: The player whose data has been loaded
        @type player: Player
        @param handler: The handler object
        @type handler: Handler
        @return: None
        """
        pass


