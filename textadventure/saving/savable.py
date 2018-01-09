from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from textadventure.player import Player
    from textadventure.handler import Handler


"""
To avoid namespace and type error, this file shouldn't import anything from the textadventure package
"""


class Savable(ABC):
    """
    A class that, if implemented, will allow you to save this class. Note that just implementing this class does\
        nothing. You must have another object/part of code that handles saving this. For this reason, if you want to\
        save all the data in your class at one point in your code, you can implement this class. Beware, if this object\
        gets into a wrong list, it could be saved.
    If you don't want to save all data in a single class, don't inherit Savable in that class, instead, create another\
        class that will store information from the original class in the new class. If you don't think you should \
        create another class, you can always put the field names that you don't want to be saved into \
        the non_serialized field
    Also, make sure that a class that inherits Thread is not saved
    Remember when loading a Savable, its __init__ will not be called

    Now that you've read all that, basically it says: "Implementing this doesn't automatically make this save and\
        if this is stored somewhere, there might be side effects from implementing this and that unless you do \
        something with non_serialized, all data will be saved"
    Data in each instance/implementation should be player specific TODO edit comment

    If you are getting a KeyError, remember to override __new__ and set any fields that are in the non_serialized list.\
        You can look in the Item in weapon.py class for an example
    """

    def __init__(self):
        self.non_serialized = []
        """A list of strings. Appending to this list allows you to stop pickler from saving a field"""

    # def __getattribute__(self, weapon):  # this is funny. I tried getting it to work with pickle. Don't try this
    #     # print("requested {} from type: {}".format(weapon, type(self)))
    #     if is_saving and weapon != "non_serialized" \
    #             and weapon in self.non_serialized:  # if this throws an error. init hasn't been called
    #         print("ignored: " + weapon)
    #         return None
    #     return super().__getattribute__(weapon)

    def __getstate__(self):
        # thanks https://stackoverflow.com/questions/6313421/can-i-mark-variables-as-transient-so-they-wont-be-pickled
        state = dict(self.__dict__)
        for item in self.non_serialized:
            del state[item]

        return state

    @abstractmethod
    def before_save(self, player: 'Player', handler: 'Handler'):
        """
        Called before the data will be saved. Override to do whatever you want with it.

        :param player: The player whose data will be saved
        :param handler: The handler object
        # :return: [0] is True if you can save, [0] is False if you can't and [1] will be the reason why
        :return: None
        """
        pass

    @abstractmethod
    def on_load(self, player: 'Player', handler: 'Handler'):
        """
        Called when the object is loaded into the player's handled_object
        this should not be called from __init__ and should and will only be called when unserializing/unpickling data\
        (that's handled for you)

        :param player: The player whose data has been loaded
        :param handler: The handler object
        :return: None
        """
        pass


class HasSavable(ABC):  # TODO do we actually need this class at all? Or can we just use the savables dict in Handler?
    """
    Can be used for classes that don't actually inherit Savable, but have a savable object
    """
    def __init__(self, savable: Optional[Savable]):
        """
        Constructor for a HasSavable instance which should be called by superclasses. When created, this class
        and other subclasses aren't expected to add the Savable to the dictionary at handler.savables. Of course,
        if the Savable is None, there's no point in putting it at handler.savables.

        :param savable: A savable that should stick with the instance and the save file forever.It is optional because
                when None, that means that this can't be saved or shouldn't be saved. The savable should save
                important things from this class and basically handle the saving and loading of this class.
        """

        self.savable = savable if savable is not None else self._create_savable()
        """Contains the Savable object that is used to saved data on this object. The point of this field is
        to provide an access point to the savable object meaning that interacting with this object regularly
        isn't what you should be doing. This should be used upon the initialization of this object and no
        other objects."""

    @abstractmethod
    def _create_savable(self) -> Optional[Savable]:
        """
        This method is protected meaning that this should be overridden by subclasses and normally, it should only
        be called in the HasSavable class

        This method should return a Savable based on the inherited subclasses and the data you want to be saved.

        If this method is implemented in a superclass, but not in a subclass, there will probably be errors if the
        game is saved and loaded so it is almost always recommended to override this if possible.

        :return: A Savable that will be set to self.savable or None.
        """
        pass


"""
This multi-line comment is just me thinking

Do we really need the HasSavable class?
Yes:
* It allows things to have savables and use their data
* It allows us to easily access the Savable object assuming the created object doesn't require one as a parameter

Do we need to allow classes to use the data stored in a Savable?
* No: We just store stuff in handler.savables and let the Savables handle stuff when loaded
* Yes: 

How are 
"""

"""
no one goes in this class right?
                                               &&&&&&&
                                        &&&&&&&&&&&&&&&&&&&&&
                                    &&&&&&&&&&         &&&&&&&&&
                                    &&&&&&   __    __      &&&&&&
                                    &&&&     @     @        &&&&&
                                    &&&&        /            &&&&
                                    &&&&       /_            &&&&
                                    &&&&                     &&&&
                                    &&&&-_   -_____-       _-&&&&
                                    &&&&  \_____-_________/  &&&&
                                    &&&&        |  |         &&&&
                                          _____/    \_______
                                    __---^                  ^---__
                               _---^                              ^---__
                              /         __                  __          \ 
                              |        ^ |                  | ^         |
                              |       /  |                  |  \        |
                              |      |   |                  |   |       |
                              |      |   |                  |   |       |
                            I am an unfinished random person. Please finish me
                                        

"""