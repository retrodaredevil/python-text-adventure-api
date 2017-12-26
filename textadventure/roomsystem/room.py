from typing import List, TYPE_CHECKING

from textadventure.utils import Point

if TYPE_CHECKING:
    from textadventure.roomsystem.house import House


class Room:
    """
    Note that a house location only includes rooms. You can create the illusion that there is an outside with rooms\
        on the outside of the main house. Kind of like webkinz world ya know?
    """
    def __init__(self, house: 'House', doorways: List[Point]):
        """
        :param house: The House object which this Room is in
        :param doorways: The list of directions the player is allowed to go while in this room excluding exits \
                            to another location.\
                            If you want the player to go from here to
        """
        self.house = house
        self.doorways = doorways

        self.entrances: List[Point] = []
        """The list of directions that the player can go to exit the location. If a player is in a room and EAST \
            is in this list and they type 'go east' they will go east of the house just like a normal location. \
            
            If you want the player to be able to come into this room when they the house location, you could add EAST \
            to this list and when they type 'go west' outside the house, they will come to this location"""
