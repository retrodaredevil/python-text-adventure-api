import sys

append = sys.path[0].replace("\\", "/").replace("/textadventure", "")  # when it's run in the command line
sys.path.append(append)

from textadventure.handler import SettingsHandler, Handler
from textadventure.message import KeyboardInput, StreamOutput;
from textadventure.player import Player
from textadventure.playersavable import PlayerSavable
from textadventure.game.entites import PlayerFriend, LauraPerson, OtherPerson, NinjaDude
from textadventure.game.locations import Entrance, InsideEntrance, EastInsideEntrance, WestInsideEntrance, \
    EntranceSpiderWebForest, CenterSpiderWebForest
from textadventure.game.data import EventsObject
from textadventure.commands import GoCommandHandler, TakeCommandHandler, PlaceCommandHandler, YellCommandHandler, \
    UseCommandHandler, NameCommandHandler, InventoryCommandHandler, LocateCommandHandler, DirectionInputHandler
from textadventure.saving import SaveCommandHandler, LoadCommandHandler


def default_load(player: 'Player', handler: 'Handler'):
    player.location = handler.get_location(Entrance)
    if player.location is None:
        raise Exception("handler.get_location mush have returned None")

    # player.handled_objects.append(PlayerFriend("Friend"))
    # player.handled_objects.append(EventsObject())
    # player.handled_objects.append(PlayerSavable())
    player[PlayerFriend] = PlayerFriend("Friend")
    player[EventsObject] = EventsObject()
    player[PlayerSavable] = PlayerSavable()


def setup():
    handler: Handler = Handler()  # if getting error. Use 3.6
    # https://docs.python.org/3/whatsnew/3.6.html#pep-526-syntax-for-variable-annotations

    stream_output = StreamOutput()
    stream_output.is_unix = "y" in input("Is your terminal unix based? (y/n) (No if you don't know) > ").lower()
    player = Player(KeyboardInput(stream_output), stream_output, None)

    # player[PlayerFriend] = PlayerFriend("Friend")

    handler.locations.extend([Entrance(), InsideEntrance(), EastInsideEntrance(), WestInsideEntrance(),
                              EntranceSpiderWebForest(), CenterSpiderWebForest()])
    handler.input_handlers.extend([GoCommandHandler(), TakeCommandHandler(), PlaceCommandHandler(),
                                   YellCommandHandler(), UseCommandHandler(), SaveCommandHandler(),
                                   LoadCommandHandler(), NameCommandHandler(), InventoryCommandHandler(),
                                   LocateCommandHandler()])
    handler.input_handlers.extend([DirectionInputHandler()])
    handler.living_things.extend([OtherPerson(), LauraPerson(), NinjaDude()])

    handler.players.append(player)
    handler.input_handlers.append(SettingsHandler(player))

    default_load(player, handler)

    player.location.on_enter(player, previous_location=None, handler=handler)

    handler.start()  # takes over this thread with infinite loop


def main():
    setup()


if __name__ == '__main__':
    main()
