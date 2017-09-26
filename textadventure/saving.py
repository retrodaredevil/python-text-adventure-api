import os
import pickle
from pathlib import Path
from pickle import UnpicklingError
from typing import Iterable, Optional

import sys

import textadventure.savable
from textadventure.command import SimpleCommandHandler
from textadventure.input import InputObject, InputHandleType
from textadventure.player import Player
from textadventure.savable import Savable
from textadventure.utils import CanDo

DEFAULT_PATH: Path = Path("./save.data")


def is_path_valid(path: Path):
    return not path.is_reserved() and os.path.splitext(path.name)[1] == ".data"


def save(handler, player: Player, path: Path=DEFAULT_PATH, override_file: bool=False) -> CanDo:
    """
    Saves the data to the file. Will overwrite data if there is any
    @param handler: The Handler object
    @param player: The player whose data will be saved
    @param path: The path to the file to save the data in
    @param override_file: True if you want to automatically override the passed file path, False otherwise
    @return: [0] is True if saved successfully, [0] is False if override_file was False and there is already a \
                    file with the path.
    """
    if not override_file and path.is_file():
        return False, "Would you like to override the file in the path {}?".format(path.absolute().name)

    to_save = []
    try:
        textadventure.savable.is_saving = True
        data = player.handled_objects  # one of the only places it can do this

        for part in data:
            if isinstance(part, Savable):  # there may be non-savables in here
                to_save.append(part)
                part.before_save(player, handler)

        with path.open("wb") as file:
            print("Going to save: {}".format(to_save))
            pickle.dump(to_save, file)
    except:
        info = sys.exc_info()
        return False, "Got error: {}, {}".format(info[0], info[1])
    finally:
        textadventure.savable.is_saving = False

    return True, "Success in saving to file: '{}'. Saved {} parts".format(path.absolute().name, len(to_save))


def load(handler, player: Player, path: 'Path'=DEFAULT_PATH) -> CanDo:
    """
    Loads the player's save data from a file
    @param handler: The Handler object
    @param path: The file path to the save data
    @param player: The player to load the data into
    @return: True if there was data to load, False otherwise
    """
    if not path.is_file():
        return False, "File was not found."
    try:
        content = pickle.load(path.open("rb"))
    except EOFError:
        return False, "The file was either empty or something is wrong with it."
    except UnpicklingError:
        return False, "Unpickling Error: {}".format(sys.exc_info()[0])
    except:
        return False, "Unexpected error: {}".format(sys.exc_info()[0])

    if content is None:
        return False, "The file's contents were null. (Or None)"

    if isinstance(content, Iterable) and type(content) is not str:
        backup = list(player.handled_objects)
        # player.handled_objects.clear()  # don't need this because well place over them anyways
        for value in content:
            if not isinstance(value, Savable):
                player.handled_objects = backup
                return False, "There was an object with the type: {} in the data.".format(type(value))
            player[type(value)] = value
            value.on_load(player, handler)
        return True, "You were able to load your save data."
    else:
        return False, "The contents of the file were in the wrong format: {}".format(type(content))


def get_path(player_input: 'InputObject') -> Optional[Path]:
    path = DEFAULT_PATH
    if len(player_input.get_arg(1, False)) != 0:  # they should only have one argument
        return None
    first_arg = player_input.get_arg(0)
    if len(first_arg) != 0:
        path = Path(first_arg[0])
    return path.absolute()


class SaveCommandHandler(SimpleCommandHandler):
    from textadventure.handler import Handler

    command_names = ["save"]
    description = "Allows you to save your game to a file. (Usually save.data)\n" \
                  "Usage: save [file name/path]"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: 'Handler', player: 'Player', player_input: 'InputObject') -> InputHandleType:
        path = get_path(player_input)
        if path is None:
            self.send_help(player)
            return InputHandleType.HANDLED
        if not is_path_valid(path):
            player.send_message("The path '{}' is not valid. The save file must end in .data".format(path.name))
            return InputHandleType.HANDLED

        result = save(handler, player, path, True)  # TODO ask the player if they want override_file to be True
        if result[0]:
            player.send_message("You successfully saved your game to '{}'".format(path.name))
        else:
            player.send_message(result[1])
        return InputHandleType.HANDLED


class LoadCommandHandler(SimpleCommandHandler):
    from textadventure.handler import Handler

    command_names = ["load"]
    description = "Allows you to load a saved game.\n" \
                  "Usage: load [file name/path]"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: 'Handler', player: 'Player', player_input: InputObject):
        path = get_path(player_input)
        if path is None:
            self.send_help(player)
            return InputHandleType.HANDLED
        if not is_path_valid(path):
            player.send_message("The path '{}' is not valid. The save file must end in .data".format(path.name))
            return InputHandleType.HANDLED
        # DONEish, most of the code above this is copy pasted. Fix it lol

        was_loaded = load(handler, player, path)

        if was_loaded[0]:
            player.send_message("You successfully loaded your game from '{}'".format(path.name))
        else:
            player.send_message(was_loaded[1])
        return InputHandleType.HANDLED

