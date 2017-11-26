"""This file will be used to test the textprint package"""
import math
from curses import wrapper, endwin
from time import sleep

from textprint.colors import Color
from textprint.section import Section
from textprint.input import InputLineUpdater
from textprint.textprinter import TextPrinter


LOADING_BAR_WIDTH = 80


debug = Section(3)
title_bar_section = Section(1)
console_section = Section(None)
input_section = Section(1)
printer = TextPrinter([input_section, console_section, title_bar_section, debug])


input_line = input_section.print(printer, "")
title_bar = title_bar_section.print(printer, "Holder")


def run_program(win):
    input_updater = InputLineUpdater(printer, input_line, win)

    debug.update_lines(printer)
    title_bar_section.update_lines(printer)
    console_section.update_lines(printer)
    input_section.update_lines(printer, flush=True)

    input_section.goto(printer, 0, 0)
    number_count = 500
    for i in range(0, number_count):

        # section loading bar
        way_there = math.floor(i / number_count * LOADING_BAR_WIDTH)
        text = Color.RED + "["
        for j in range(0, LOADING_BAR_WIDTH):
            if j < way_there:
                text += "#"
            else:
                text += " "
        text += "]" + Color.RESET
        title_bar.contents = text
        title_bar.update(printer)
        # end section loading bar
        console_section.print(printer, "Hello there: {}".format(i))
        title_bar.update(printer)

        # input_line.contents = input_updater.current_line_string()
        # # debug.print(printer, input_updater.current_line_string())
        # input_line.update(printer)
        # input_updater.goto_cursor(flush=True)  # in case we moved the cursor (unlikely since we updated input_line)\
        # #       but it could happen if the player moves their cursor

        # input_updater.update_line()  # changed commented out stuff to this
        input_updater.update()
        sleep(.02)
        if input_updater.should_exit:
            break
    while True:
        if input_updater.should_exit:
            break


if __name__ == '__main__':
    wrapper(run_program)
