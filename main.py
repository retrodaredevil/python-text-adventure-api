#!/bin/sh
''''which python3.5 1>/dev/null 2>&1 && exec python3.5 "$0" "$@" # '''
''''which python3 1>/dev/null 2>&1 && exec python3 "$0" "$@"     # '''
''''which python 1>/dev/null 2>&1 && exec python "$0" "$@" # '''
''''exec echo "You must not have python 3 installed. Make sure you have at least version 3.5" # '''
# thanks https://stackoverflow.com/a/26056481 for the above!

import sys
assert sys.version_info >= (3, 5), "Must use python 3.5 or greater. Many of the files use the typing module."

import time

from pathlib import Path

from textadventure.input.inputhandling import CommandInput, FlagData
from textadventure.saving.saving import SavePath


from ninjagame.game import NinjaGame
from textadventure.clientside.inputs import TextPrinterInputGetter, KeyboardInputGetter
from textadventure.clientside.outputs import TextPrinterOutput, LocationTitleBarManager, ImmediateStreamOutput
from textadventure.mainclass import ClientSideMain
from textadventure.player import Player
from textprint.colors import Color
from textprint.inithelper import curses_init, std_init, curses_end, add_interrupt_handler, colorama_init
from textprint.input import InputLineUpdater
from textprint.section import Section
from textprint.textprinter import TextPrinter

"""
This file is an example game for my text adventure api using the ninjagame package

This file is not meant to be imported which is why it is not in any package right now
"""


save_path = SavePath(Path("./save.dat.d"))


def setup_fancy():
    import curses

    # https://docs.python.org/3/whatsnew/3.6.html#pep-526-syntax-for-variable-annotations

    def start(stdscr):
        curses_init()
        std_init(stdscr)
        colorama_init()

        input_section = Section(None, fill_up_left_over=False)  # we want to allow it to go for as many lines it needs
        print_section = Section(None, fake_line=(Color.BLUE >> "~"))
        title_section = Section(1)
        printer = TextPrinter([input_section, print_section, title_section], print_from_top=False, stdscr=stdscr)
        printer.update_dimensions()
        # print_section.fake_line = Color.RED + Color.BOLD + "|" + (" " * (printer.dimensions[1] - 3)) + "|"

        updater = InputLineUpdater(printer, input_section.println(printer, "", flush=True), stdscr)
        player_input = TextPrinterInputGetter(updater)
        # input_manager = InputLineUpdaterManager(updater)  # calls updater's update
        output = TextPrinterOutput(printer, print_section)
        player = Player(player_input, output, None)

        add_interrupt_handler(lambda: updater.current_line().clear())  # clear line when CTRL+C is pressed

        title_manager = LocationTitleBarManager(player, printer, title_section.println(printer, ""))

        main_instance = ClientSideMain(NinjaGame(), [player_input, output, title_manager], player, save_path)

        main_instance.start()
        while True:
            main_instance.update()
            time.sleep(.001)  # let the cpu rest a little bit

    try:
        scanner = curses.initscr()
        start(scanner)
    finally:
        curses_end()


def setup_simple():
    colorama_init()
    print()

    player_input = KeyboardInputGetter()
    player_input.daemon = True
    player_input.start()

    output = ImmediateStreamOutput()

    player = Player(player_input, output, None)

    main_instance = ClientSideMain(NinjaGame(), [output], player, save_path)
    main_instance.start()
    while True:
        main_instance.update()
        time.sleep(.2)


def auto_flag_setup():
    command = CommandInput(CommandInput.join(sys.argv))
    options = {
        ("rest", "r"): 1,
        ("simple", "windows", "dos"): 0,
        ("file", "f", "save", "path"): 1,
        ("clean", "no_load"): 0,
        ("user", "u", "player"): 1  # TODO
    }
    flag_data = FlagData(command, options)

    rest = 0.0
    string_rest = flag_data.get_flag("rest")
    if string_rest:
        try:
            rest = float(string_rest)
        except ValueError:
            print("{} is not a valid number for rest.".format(string_rest))
            sys.exit(1)

    string_file = flag_data.get_flag("file")
    if string_file:
        global save_path
        save_path = SavePath(Path(string_file))

    if flag_data.get_flag("simple"):
        setup_simple()
    else:
        try:
            import curses
            import pyparsing
        except ModuleNotFoundError:
            print("Unable to load curses or pyparsing library. Initializing simple instead of fancy")
            setup_simple()
        else:
            setup_fancy()


def main():
    try:
        auto_flag_setup()
    except KeyboardInterrupt:
        print("Ended program with a keyboard interrupt")
        sys.exit(0)


if __name__ == '__main__':
    main()
