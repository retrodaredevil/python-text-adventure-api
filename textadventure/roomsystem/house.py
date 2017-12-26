from typing import List, TYPE_CHECKING

from textadventure.handler import Handler
from textadventure.location import Location
from textadventure.player import Player
from textadventure.utils import Point

if TYPE_CHECKING:
    from textadventure.roomsystem.room import Room


# I don't think this'll be abstract so don't put no-inspect
class House(Location):
    """
    A house is basically a list of rooms with its own coordinate system
    """

    def __init__(self, name, description, point, rooms: List['Room']):
        super().__init__(name, description, point)

        self.rooms = rooms

    def go_to_other_location(self, handler: Handler, new_location: Location, direction: Point, player: Player):
        pass

    # TODO actually implement methods of this class
