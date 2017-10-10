from typing import List

from textadventure.house.room import Room
from textadventure.location import Location


class House(Location):
    def __init__(self, name, description, point):
        super().__init__(name, description, point)

        self.rooms: List[Room]
