from abc import abstractmethod, ABC
from typing import Optional

from textadventure.handler import Handler
from textadventure.holder import Holder
from textadventure.player import Player
from textadventure.savable import Savable
from textadventure.utils import are_mostly_equal, CanDo


class FiveSensesHandler(ABC):
    """
    The methods don't return a CanDo because locations need to be able to handle these and a Item's can_<sense>methods\
    solve this problem
    """

    @abstractmethod
    def see(self, handler: Handler, player: Player):
        pass

    @abstractmethod
    def listen(self, handler: Handler, player: Player):
        pass

    @abstractmethod
    def feel(self, handler: Handler, player: Player):
        pass

    @abstractmethod
    def smell(self, handler: Handler, player: Player):
        pass

    @abstractmethod
    def taste(self, handler: Handler, player: Player):
        pass


class Item(Savable, FiveSensesHandler):
    # doesn't have implementation for any methods of FiveSensesHandler so it's abstract
    CANNOT_SEE: CanDo = (False, "You can't see that")  # can_reference may also return this # used in some commands
    CANNOT_LISTEN: CanDo = (False, "You can't listen to this")
    CANNOT_FEEL: CanDo = (False, "You can't feel this")
    CANNOT_SMELL: CanDo = (False, "You can't smell this")
    CANNOT_TASTE: CanDo = (False, "You can't taste this")
    # CANNOT_USE: CanDo = (False, "You can't use this")
    CANNOT_USE_DO_NOT_HAVE: CanDo = (False, "You don't have this weapon")
    CANNOT_TAKE: CanDo = (False, "You can't take this")
    CANNOT_TAKE_ON_PERSON: CanDo = (False, "You already have this")
    CANNOT_PUT: CanDo = (False, "You can't place this")
    CANNOT_PUT_IN_LOCATION: CanDo = (False, "It's already placed")  # may be returned from can_put

    non_serialized = ["holder"]
    """
    An object that's handled by the object containing the Item

    For all the can methods, they return a CanDo which is a Tuple[bool, str]
    For any can method, you should make sure that the player can reference this Item using can_reference
    For calling any of the five senses methods, you should make sure the player is able to do that on this weapon
    """

    def __new__(cls, *args, **kwargs):
        """Needed for saving and so the non_serialized attribute actually works"""
        instance = object.__new__(cls)
        for item in cls.non_serialized:  # weapon is a string
            setattr(instance, item, None)
        return instance

    def __init__(self, name: str, needs_light_to_see: bool):
        """
        An object that is in a location with properties that define how it should react when players type commands
        Once created, to change/add the holder call the change_holder method
        :param name: The name of the object
        :param needs_light_to_see: Should almost always be true
        """
        super().__init__()  # for multiple inheritance
        self.name = name
        self.holder: Optional[Holder] = None  # noinspection PyTypeChecker # can be player, location etc
        self.non_serialized = self.__class__.non_serialized
        self.__needs_light = needs_light_to_see

    def __str__(self):
        return self.name

    def change_holder(self, previous_holder: Optional[Holder], new_holder: Holder) -> bool:
        """
        The method that should be called when you want to change the holder (Don't change holder directly)
        When overridden, to change the holder, you should always call the superclass instead of doing it yourself
        :param previous_holder: The previous holder (should be the same as self.holder but pass it anyway)
        :param new_holder: The new holder
        :return: Returns True if the holder was successfully changed. False if it was not (overriding subclasses may or\
                        may not react to the changing or trying to change of the holder (You shouldn't react)
        :param previous_holder test
        """
        assert new_holder is not None, "Why would you change the holder to None?"
        # change in future if needs to delete weapon.

        self.holder = new_holder
        if previous_holder is not None and self in previous_holder.items:
            previous_holder.items.remove(self)
        if self not in new_holder.items:
            new_holder.items.append(self)
        return True

    def before_save(self, player, handler):
        """Note that player may not be the holder."""
        # print("Saving: {}".format(type(self)))

    def on_load(self, player, handler):
        """Note that player may not be the holder."""
        self.holder = player

    def is_reference(self, reference: str) -> bool:
        """
        Should be called before can_reference
        :param reference: The string used to reference this Item
        :return: A boolean telling whether or not the string is close enough to reference this Item
        """
        return are_mostly_equal(self.name, reference)

    def can_reference(self, player: Player) -> CanDo:
        from textadventure.location import Location
        if isinstance(self.holder, Location):
            if self.holder.is_lit_up() or not self.__needs_light:
                return True, "You can reference this and self.holder is a Location"
        if self.holder == player:
            return True, "You have the thing on you"
        return self.__class__.CANNOT_SEE

    def can_see(self, player: Player) -> CanDo:
        from textadventure.location import Location
        if isinstance(self.holder, Location):
            return True, "You can see this since self.holder is a Location"
        elif self.holder == player:
            return False, "You cannot look at something on you!"
        return self.__class__.CANNOT_SEE

    def can_listen(self, player: Player) -> CanDo:
        return self.__class__.CANNOT_LISTEN

    def can_feel(self, player: Player) -> CanDo:
        return self.__class__.CANNOT_FEEL

    def can_smell(self, player: Player) -> CanDo:
        return self.__class__.CANNOT_SMELL

    def can_taste(self, player: Player) -> CanDo:
        return self.__class__.CANNOT_TASTE

    def can_take(self, player: Player) -> CanDo:
        if self.holder == player:
            return self.__class__.CANNOT_TAKE_ON_PERSON
        return self.__class__.CANNOT_TAKE

    def can_put(self, player: Player) -> CanDo:
        from textadventure.location import Location
        if isinstance(self.holder, Location):  # cannot place because player doesn't have it
            return self.__class__.CANNOT_PUT_IN_LOCATION
        return self.__class__.CANNOT_PUT

    def can_use(self, player: Player) -> CanDo:
        if self in player.items:
            return True, "You can use this because you have it"
        else:
            return self.__class__.CANNOT_USE_DO_NOT_HAVE

    @abstractmethod
    def use_item(self, handler: Handler, player: Player) -> bool:
        """
        By default does nothing. can_use should only return true if this has been overridden
        This method should be called by the Location class and from no where else
        :param handler: The handler object
        :param player: The player using the weapon
        :return: True if it was successful in using the weapon. If false, should have sent an error message already
        """
        pass
