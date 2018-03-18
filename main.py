import curses
import sys

assert sys.version_info >= (3, 5), "Must use python 3.5 or greater. Many of the files use the typing module."

from ninjagame.game import NinjaGame
from textadventure.clientside.inputs import TextPrinterInputGetter, InputLineUpdaterManager
from textadventure.clientside.outputs import TextPrinterOutput, LocationTitleBarManager
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


def setup():

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
        output = TextPrinterOutput(printer, print_section)
        player = Player(player_input, output, None, None)

        add_interrupt_handler(lambda: updater.current_line().clear())  # clear line when CTRL+C is pressed

        title_manager = LocationTitleBarManager(player, printer, title_section.println(printer, ""))
        input_manager = InputLineUpdaterManager(updater)  # calls updater's update

        main_instance = ClientSideMain(NinjaGame(), [input_manager, output, title_manager], player)

        main_instance.start()
        while True:
            main_instance.update()

    try:
        scanner = curses.initscr()
        start(scanner)
    finally:
        curses_end()


def main():
    setup()


if __name__ == '__main__':
    main()
