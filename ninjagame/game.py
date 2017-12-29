from textadventure.customgame import CustomGame
from textadventure.handler import Handler


class NinjaGame(CustomGame):

    def __init__(self):
        super().__init__("Trail of Ninjas")

    def add_other(self, handler: Handler):
        pass

    def create_custom_input_handlers(self):
        return []

    def create_custom_managers(self, handler: Handler):
        return []

    def create_locations(self, handler: Handler):
        return []
