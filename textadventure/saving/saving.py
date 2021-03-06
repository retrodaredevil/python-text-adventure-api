import pickle
import sys
from pathlib import Path

from pickle import UnpicklingError
from typing import Union, Any, TYPE_CHECKING

from textadventure.utils import CanDo

if TYPE_CHECKING:
    from textadventure.player import Player


def save_data(data, path: Path) -> CanDo:
    """
    Saves the data to file opened from path and does nothing else. (Doesn't call methods, doesn't check if Savable)

    :param data: The data that you want to save to a file.
    :param path: The path to the file to open
    :return: A CanDo where [0] represents whether or not it was successful or not and [1] tells the person who
            saved the data if they were successful. [1] should normally be printed unlike most other CanDo[1]
    """
    try:
        if not path.parent.exists():
            path.parent.mkdir()
        with path.open("wb") as file:
            # print("Going to save: {}".format(to_save))
            pickle.dump(data, file)
    except IOError:
        info = sys.exc_info()
        return False, "error: '{}'".format(info)
    return True, "You successfully saved your data to {}.".format(path.absolute())


def load_data(path: Path) -> Union[Any, str]:
    """
    Loads data from a file returning the contents of that file or returning a string representing an error

    Because this returns a string for an error, this will also return a string if the contents of the file are a
    string. The returned string will be an error message saying the data cannot be a string

    :param path: The path to the file to open
    :return: The content if the file was loaded successfully or an error message
    """
    if not path.is_file():
        return "File was not found."
    try:
        content = pickle.load(path.open("rb"))
    except EOFError:  # End of File Error
        return "The file was either empty or something is wrong with it."
    except UnpicklingError:
        return "Unpickling Error: {}".format(sys.exc_info()[0])
    # except:  # we want to see this error fully. And this error is a bad one so we commented this out
    #     return False, "Unexpected error: {}".format(sys.exc_info()[0])

    if content is None:
        return "The file's contents were null. (Or None) Why anyone would pickle a NoneType is beyond me."
    if isinstance(content, str):
        return "The file's contents cannot be a string."

    return content


class SavePath:
    """
    A class that represents a path object and has helper methods but doesn't actually do any of the work in saving data.

    This object is also immutable
    """
    def __init__(self, path: Path):
        """
        :param path: The path
        """
        self._path = path
        """This is private because no one should need to see this or need to change it"""

        # assert not self.path.is_file() and not self.path.is_reserved()

    def __str__(self):
        return self.__class__.__name__ + "('" + str(self._path.absolute()) + "')"

    def is_valid(self) -> CanDo:
        if self._path.is_file():
            return False, "The save path cannot be a file that already exists. " \
                          "It must be a directory or a non existent file."
        if self._path.is_reserved():
            return False, "You can't use this path because it's reserved."

        return True, "This is a valid path"

    def get_handler_path(self):
        return self._path.joinpath("handler.dat")

    def get_player_folder(self):
        return self._path.joinpath("players")

    def get_player_path(self, player: 'Player'):
        return self.get_player_folder().joinpath(str(player.uuid) + ".dat")


'''
DEFAULT_PATH = Path("./save.dat")


def is_path_valid(path: Path):
    return not path.is_reserved() and os.path.splitext(path.name)[1] == ".dat"


def save(handler: 'Handler', player: Player, path: Path = DEFAULT_PATH, override_file: bool = False) -> CanDo:
    """
    Saves the data to the file. Will overwrite data if there is any

    :param handler: The Handler object
    :param player: The player whose data will be saved
    :param path: The path to the file to save the data in
    :param override_file: True if you want to automatically override the passed file path, False otherwise
    :return: [0] is True if saved successfully, [0] is False if override_file was False and there is already a
             file with the path.
    """
    if not override_file and path.is_file():
        return False, "Please specify that you would like to override the file using --override".format(
            path.absolute().name)

    # noinspection PyBroadException
    try:
        to_save = player.savable
        to_save.before_save(player, handler)

        with path.open("wb") as file:
            print("Going to save: {}".format(to_save))
            pickle.dump(to_save, file)
    except Exception:
        info = sys.exc_info()
        return False, "Got error: {}, {}".format(info[0], info[1])

    return True, "Success in saving to file: '{}'.".format(path.absolute().name)


def load(handler: 'Handler', player: Player, path: Path = DEFAULT_PATH) -> CanDo:
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
        open_file = path.open('rb')
        content = pickle.load(open_file)
    except EOFError:  # End of File Error
        return False, "The file was either empty or something is wrong with it."
    except UnpicklingError:
        return False, "Unpickling Error: {}".format(sys.exc_info()[0])
    # except:  # we want to see this error fully. And this error is a bad one so we commented this out
    #     return False, "Unexpected error: {}".format(sys.exc_info()[0])

    if content is None:
        return False, "The file's contents were null. (Or None) Why anyone would pickle a NoneType is beyond me."

    if isinstance(content, Savable):
        # backup = list(player.handled_objects)
        # # player.handled_objects.clear()  # don't need this because well place over them anyways
        # for value in content:
        #     if not isinstance(value, Savable):
        #         player.handled_objects = backup
        #         return False, "There was an object with the type: {} in the data.".format(type(value))
        #     player[type(value)] = value
        #     value.on_load(player, handler)
        content.on_load(player, handler)
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



class SaveCommandHandler(SimpleCommandHandler):
    command_names = ["save"]
    description = "Allows you to save your ninjagame to a file. (Usually save.data)\n" \
                  "Usage: save [file name/path]"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: 'Handler', sender: CommandSender, command_input: CommandInput) -> InputHandleType:
        if not isinstance(sender, Player):
            sender.send_message("You must be a player to save the game. In the future, you can save handler")
            return InputHandleType.HANDLED

        path = get_path(command_input)
        if path is None:
            self.send_help(sender)
            return InputHandleType.HANDLED
        if not is_path_valid(path):
            sender.send_message("The path '{}' is not valid. The save file must end in .data".format(path.name))
            return InputHandleType.HANDLED

        result = save(handler, sender, path, True)  # TODO ask the player if they want override_file to be True
        if result[0]:
            sender.send_message("You successfully saved your game to '{}'".format(path.name))
        else:
            sender.send_message(result[1])
        return InputHandleType.HANDLED


class LoadCommandHandler(SimpleCommandHandler):
    command_names = ["load"]
    description = "Allows you to load a saved game.\n" \
                  "Usage: load [file name/path]"

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

    def _handle_command(self, handler: 'Handler', sender: CommandSender, command_input: CommandInput):
        if not isinstance(sender, Player):
            sender.send_message("You must be a player to save the game. In the future, you can save handler")
            return InputHandleType.HANDLED

        path = get_path(command_input)
        if path is None:
            self.send_help(sender)
            return InputHandleType.HANDLED
        if not is_path_valid(path):
            sender.send_message("The path '{}' is not valid. The save file must end in .data".format(path.name))
            return InputHandleType.HANDLED
        # DONEish, most of the code above this is copy pasted. Fix it lol

        was_loaded = load(handler, sender, path)

        if was_loaded[0]:
            sender.send_message("You successfully loaded your game from '{}'".format(path.name))
        else:
            sender.send_message(was_loaded[1])
        return InputHandleType.HANDLED
'''
