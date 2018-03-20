import sys

from textadventure.input.inputhandling import CommandInput

assert sys.version_info >= (3, 5), "Must use python 3.5 or greater. Many of the files use the typing module."

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
        player = Player(player_input, output, None, None)

        add_interrupt_handler(lambda: updater.current_line().clear())  # clear line when CTRL+C is pressed

        title_manager = LocationTitleBarManager(player, printer, title_section.println(printer, ""))

        main_instance = ClientSideMain(NinjaGame(), [player_input, output, title_manager], player)

        main_instance.start()
        while True:
            main_instance.update()

    try:
        scanner = curses.initscr()
        start(scanner)
    finally:
        curses_end()


def setup_simple():
    colorama_init()

    player_input = KeyboardInputGetter()
    player_input.daemon = True
    player_input.start()

    output = ImmediateStreamOutput()

    player = Player(player_input, output, None, None)

    main_instance = ClientSideMain(NinjaGame(), [output], player)
    main_instance.start()
    while True:
        main_instance.update()


def main():
    command = CommandInput(CommandInput.join(sys.argv))
    flags = command.get_flags()
    if "simple" in flags:
        setup_simple()
    else:
        try:
            import curses
        except ModuleNotFoundError:
            print("Unable to load curses library. Initializing simple instead of fancy")
            setup_simple()
        else:
            setup_fancy()


if __name__ == '__main__':
    main()
