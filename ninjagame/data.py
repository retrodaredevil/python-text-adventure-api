"""
This file is used for data specific things.
It was moved from player.py to locations.py because it wasn't for the api (it was for the game)
Then, it was moved from locations.py to here because of importing errors
"""
from textadventure.savable import Savable


class EventsObject(Savable):
    """
    An class that holds most of the data for the player but not all data
    Basically holds a bunch of one way flags.
    This class is used as per player data meaning that the values in this class may determine what a certain player\
        can or can't do. Just because one player can do something doesn't mean another can.
    Obviously, if you are making your own game, you wouldn't use this class, you would use a similar one to suit your \
        needs
    """

    def __init__(self):
        super().__init__()
        self.been_introduced_to_furry = False
        self.knows_laura = False  # note: also used to tell if Laura should have an unknown name
        self.has_cleared_spider_webs_at_entrance = False
        self.has_been_in_center_spider_web_forest = False

    def on_load(self, player, handler):
        pass

    def before_save(self, player, handler):
        pass
