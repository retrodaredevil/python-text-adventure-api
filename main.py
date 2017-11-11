# import sys
#
# append = sys.path[0].replace("\\", "/").replace("/textadventure", "")  # when it's run in the command line
# sys.path.append(append)
# above was used for when main.py was not inside the root of the project

from ninjagame.data import EventsObject
from ninjagame.entites import PlayerFriend, LauraPerson, OtherPerson, NinjaDude

from ninjagame.locations import Entrance, InsideEntrance, EastInsideEntrance, WestInsideEntrance, \
    EntranceSpiderWebForest, CenterSpiderWebForest, EastCenterSpiderWebForest
from ninjagame.managing import NinjaGamePropertyManager
from textadventure.actions import EntityActionToEntityManager
from textadventure.battling.commands import AttackCommandHandler
from textadventure.battling.managing import HostileEntityManager, BattleManager, DamageActionManager
from textadventure.commands import GoCommandHandler, TakeCommandHandler, PlaceCommandHandler, YellCommandHandler, \
    UseCommandHandler, NameCommandHandler, InventoryCommandHandler, LocateCommandHandler, DirectionInputHandler, \
    HelpCommandHandler
from textadventure.handler import Handler
from textadventure.inputhandlers import SettingsHandler
from textadventure.message import KeyboardInput, StreamOutput
from textadventure.player import Player
from textadventure.playersavable import PlayerSavable
from textadventure.saving import SaveCommandHandler, LoadCommandHandler

"""
This file is an example game for my text adventure api using the ninjagame package
"""


def default_load(player: Player, handler: Handler):
    player.location = handler.get_location(Entrance)

    assert player.location is not None, "handler.get_location returned None. Make sure you set up locations correctly."

    # player.handled_objects.append(PlayerFriend("Friend"))  # not recommended way of doing this
    # player.handled_objects.append(EventsObject())
    # player.handled_objects.append(PlayerSavable())
    player[PlayerFriend] = PlayerFriend("Friend")  # not used as a magic string
    player[EventsObject] = EventsObject()
    player[PlayerSavable] = PlayerSavable()


def setup():
    handler = Handler()
    # https://docs.python.org/3/whatsnew/3.6.html#pep-526-syntax-for-variable-annotations

    stream_output = StreamOutput()
    stream_output.is_unix = "y" in input("Is your terminal unix based? (y/n) (No if you don't know) > ").lower()
    player = Player(KeyboardInput(stream_output), stream_output, None)  # "Untitled.notebook") using as name glitches

    # player[PlayerFriend] = PlayerFriend("Friend")

    handler.locations.extend([Entrance(), InsideEntrance(), EastInsideEntrance(), WestInsideEntrance(),
                              EntranceSpiderWebForest(), CenterSpiderWebForest(), EastCenterSpiderWebForest(handler)])
    handler.input_handlers.extend([GoCommandHandler(), TakeCommandHandler(), PlaceCommandHandler(),
                                   YellCommandHandler(), UseCommandHandler(), SaveCommandHandler(),
                                   LoadCommandHandler(), NameCommandHandler(), InventoryCommandHandler(),
                                   LocateCommandHandler(), HelpCommandHandler(), AttackCommandHandler()])
    handler.input_handlers.extend([DirectionInputHandler()])
    handler.living_things.extend([OtherPerson(), LauraPerson(), NinjaDude()])

    handler.entities.append(player)
    handler.input_handlers.append(SettingsHandler(player))
    handler.managers.extend([HostileEntityManager(), EntityActionToEntityManager(), BattleManager(),
                             DamageActionManager(), NinjaGamePropertyManager()])

    default_load(player, handler)

    player.location.on_enter(player, previous_location=None, handler=handler)

    handler.start()  # takes over this thread with infinite loop


def main():
    setup()


if __name__ == '__main__':
    main()
