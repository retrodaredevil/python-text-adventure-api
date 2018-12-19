import sys
import time

from pathlib import Path

from textadventure.input.inputhandling import CommandInput, FlagData
from textadventure.saving.saving import SavePath


from ninjagame.game import NinjaGame
from textadventure.clientside.inputs import TextPrinterInputGetter, KeyboardInputGetter
from textadventure.clientside.outputs import TextPrinterOutput, LocationTitleBarManager, ImmediateStreamOutput, \
    OutputNotifierSender
from textadventure.mainclass import ClientSideMain
from textadventure.player import Player
from textadventure.sending.message import Message, MessageType
from textprint.colors import Color
from textprint.inithelper import curses_init, std_init, curses_end, add_interrupt_handler, colorama_init
from textadventure.handler import PlayerHandler

"""
This file is an example game for my text adventure api using the ninjagame package

This file is not meant to be imported which is why it is not in any package right now
"""


def create_fancy_player(stdscr, savable):
    from textprint.input import InputLineUpdater
    from textprint.section import Section
    from textprint.textprinter import TextPrinter

    curses_init()
    std_init(stdscr)
    colorama_init()

    input_section = Section(None, fill_up_left_over=False)  # we want to allow it to go for as many lines it needs
    temp_section = Section(None, fill_up_left_over=False)
    print_section = Section(None, fake_line=(Color.BLUE >> "~"))
    title_section = Section(1)
    printer = TextPrinter([input_section, temp_section, print_section, title_section],
                          print_from_top=False, stdscr=stdscr)
    printer.update_dimensions()
    # print_section.fake_line = Color.RED + Color.BOLD + "|" + (" " * (printer.dimensions[1] - 3)) + "|"

    updater = InputLineUpdater(printer, input_section.println(printer, "", flush=True), stdscr)
    player_input = TextPrinterInputGetter(updater)
    # input_manager = InputLineUpdaterManager(updater)  # calls updater's update
    output = OutputNotifierSender(TextPrinterOutput(printer, print_section),
                                  lambda: temp_output.section.clear_lines(printer, flush=True))
    temp_output = TextPrinterOutput(printer, temp_section)
    player = Player(player_input, output, savable)

    def interrupt_handler():
        if updater.current_line().is_clear():
            temp_output.send_message(Message(Color.YELLOW >> "Press CTRL+D to exit", message_type=MessageType.IMMEDIATE))
            print_section.update_lines(printer, flush=True, force_reprint=True)
        else:
            updater.current_line().clear()

    add_interrupt_handler(interrupt_handler)  # clear line when CTRL+C is pressed

    title_manager = LocationTitleBarManager(player, printer, title_section.println(printer, ""))

    return player, [player_input, output, temp_output, title_manager], lambda: curses_end()


def create_simple_player(savable):

    colorama_init()
    print()

    player_input = KeyboardInputGetter()
    player_input.start()

    output = ImmediateStreamOutput()

    player = Player(player_input, output, savable)

    return player, [output], lambda: None


def auto_flag_setup():
    command = CommandInput(CommandInput.join(sys.argv))
    options = {
        ("rest", "r"): 1,
        ("simple", "windows", "dos"): 0,
        ("file", "f", "save", "path"): 1,
        ("clean", "no_load"): 0,
        ("user", "u", "player", "name"): 1
    }
    flag_data = FlagData(command, options)

    rest = 0.001
    string_rest = flag_data.get_flag("rest")
    if string_rest is not None:
        try:
            rest = float(string_rest)
        except ValueError:
            print("'{}' is not a valid number for rest.".format(string_rest))
            sys.exit(1)
    if rest > 1:
        print("Rest cannot be greater than 1. Rest is the amount of time in seconds it waits to update.")
        print("Making this greater than 1 makes the game unresponsive for too long of a period.")
        sys.exit(1)

    string_file = flag_data.get_flag("file")
    save_path = SavePath(Path("./save.dat.d"))
    if string_file:
        save_path = SavePath(Path(string_file))

    is_clean = flag_data.get_flag("clean")  # should we load data?

    player_handler = PlayerHandler(save_path)
    player_savable = None

    result = player_handler.load_player_savables()  # load these anyway

    player_name = flag_data.get_flag("user")
    if player_name is not None:
        if is_clean:
            print("Error: Using --clean flag but also specifying a player to load.")
            sys.exit(1)
        if not result[0]:
            print(result[1])
            sys.exit(1)
        player_savable = player_handler.get_player_savable(player_name)
        if player_savable is None:
            print("Unable to find player with name: '{}'".format(player_name))
            sys.exit(1)
        else:
            print("Successfully loaded player: '{}'".format(player_savable.name))

    if flag_data.get_flag("simple"):
        # setup_simple(player_savable)
        information = create_simple_player(player_savable)
    else:
        try:
            import curses
            import pyparsing
        except ModuleNotFoundError:
            print("Unable to load curses or pyparsing library. Initializing simple instead of fancy")
            # setup_simple(player_savable)
            information = create_simple_player(player_savable)
        else:
            # setup_fancy(player_savable)
            information = create_fancy_player(curses.initscr(), player_savable)

    player, custom_managers, end_function = information
    try:
        main_instance = ClientSideMain(NinjaGame(), custom_managers, player, save_path, rest=rest,
                                       player_handler=player_handler)
        main_instance.start()

        while True:
            main_instance.update()
            time.sleep(rest)
    finally:
        end_function()


def main():
    try:
        auto_flag_setup()
    except KeyboardInterrupt:
        print("Ended program with a keyboard interrupt")
        sys.exit(0)
    finally:
        try:
            curses_end()
        except ImportError:
            pass


if __name__ == '__main__':
    main()
