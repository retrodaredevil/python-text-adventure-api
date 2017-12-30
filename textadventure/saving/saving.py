import os
import pickle
import sys
from pathlib import Path
from pickle import UnpicklingError
from typing import Iterable, Optional, TYPE_CHECKING

from textadventure.commands.command import SimpleCommandHandler
from textadventure.input.inputhandling import CommandInput, InputHandleType
from textadventure.player import Player
from textadventure.saving.savable import Savable
from textadventure.utils import CanDo

if TYPE_CHECKING:
    from textadventure.handler import Handler

DEFAULT_PATH = Path("./save.data")


def is_path_valid(path: Path):
    return not path.is_reserved() and os.path.splitext(path.name)[1] == ".data"


def save(handler, player: Player, path: Path = DEFAULT_PATH, override_file: bool = False) -> CanDo:
    """
    Saves the data to the file. Will overwrite data if there is any

    :param handler: The Handler object
    :param player: The player whose data will be saved
    :param path: The path to the file to save the data in
    :param override_file: True if you want to automatically override the passed file path, False otherwise
    :return: [0] is True if saved successfully, [0] is False if override_file was False and there is already a \
                    file with the path.
    """
    if not override_file and path.is_file():
        return False, "Please specify that you would like to override the file using --override".format(
            path.absolute().name)

    to_save = []
    # noinspection PyBroadException
    try:
        data = player.handled_objects  # one of the only places it can do this

        for part in data:
            if isinstance(part, Savable):  # there may be non-savables in here
                to_save.append(part)
                part.before_save(player, handler)

        with path.open("wb") as file:
            print("Going to save: {}".format(to_save))
            pickle.dump(to_save, file)
    except Exception:
        info = sys.exc_info()
        return False, "Got error: {}, {}".format(info[0], info[1])

    return True, "Success in saving to file: '{}'. Saved {} parts".format(path.absolute().name, len(to_save))


def load(handler, player: Player, path: Path = DEFAULT_PATH) -> CanDo:
    """
    Loads the player's save data from a file

    :param handler: The Handler object
    :param path: The file path to the save data
    :param player: The player to load the data into
    :return: True if there was data to load, False otherwise
    """
    if not path.is_file():
        return False, "File was not found."
    try:
        content = pickle.load(path.open("rb"))
    except EOFError:  # End of File Error
        return False, "The file was either empty or something is wrong with it."
    except UnpicklingError:
        return False, "Unpickling Error: {}".format(sys.exc_info()[0])
    # except:  # we want to see this error fully. And this error is a bad one so we commented this out
    #     return False, "Unexpected error: {}".format(sys.exc_info()[0])

    if content is None:
        return False, "The file's contents were null. (Or None) Why anyone would pickle a NoneType is beyond me."

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


def get_path(command_input: CommandInput) -> Optional[Path]:
    """
    This method assumes that the input should only have one argument that is at index 0 while calling get_arg and\
    doesn't ignore unimportant

    :param command_input:
    :return:
    """
    path = DEFAULT_PATH
    if len(command_input.get_arg(1, False)) != 0:  # they should only have one argument
        return None
    first_arg = command_input.get_arg(0)
    if len(first_arg) != 0:
        path = Path(first_arg[0])
    return path.absolute()


class Saving:
    def __init__(self, path: Path):
        """
        Creates a Saving object

        :param path: The path to the directory that it will save in
        """
        self.path = path

        assert not self.path.is_file() and not self.path.is_reserved()

    def _get_handler_path(self):
        return self.path.joinpath("handler.dat")

    def _get_player_path(self, player: Player):
        return self.path.joinpath(player.name + ".player.dat")

    def save_handler(self, handler: 'Handler'):
        path = self._get_handler_path()


class SaveCommandHandler(SimpleCommandHandler):
    command_names = ["save"]
    description = "Allows you to save your ninjagame to a file. (Usually save.data)\n" \
                  "Usage: save [file name/path]"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: 'Handler', player: Player, command_input: CommandInput) -> InputHandleType:
        path = get_path(command_input)
        if path is None:
            self.send_help(player)
            return InputHandleType.HANDLED
        if not is_path_valid(path):
            player.send_message("The path '{}' is not valid. The save file must end in .data".format(path.name))
            return InputHandleType.HANDLED

        result = save(handler, player, path, True)  # TODO ask the player if they want override_file to be True
        if result[0]:
            player.send_message("You successfully saved your ninjagame to '{}'".format(path.name))
        else:
            player.send_message(result[1])
        return InputHandleType.HANDLED


class LoadCommandHandler(SimpleCommandHandler):
    command_names = ["load"]
    description = "Allows you to load a saved ninjagame.\n" \
                  "Usage: load [file name/path]"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: 'Handler', player: Player, command_input: CommandInput):
        path = get_path(command_input)
        if path is None:
            self.send_help(player)
            return InputHandleType.HANDLED
        if not is_path_valid(path):
            player.send_message("The path '{}' is not valid. The save file must end in .data".format(path.name))
            return InputHandleType.HANDLED
        # DONEish, most of the code above this is copy pasted. Fix it lol

        was_loaded = load(handler, player, path)

        if was_loaded[0]:
            player.send_message("You successfully loaded your ninjagame from '{}'".format(path.name))
        else:
            player.send_message(was_loaded[1])
        return InputHandleType.HANDLED
