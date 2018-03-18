"""This file will be used to test the textprint package"""
from curses import wrapper

from math import floor

from textprint.colors import Color
from textprint.inithelper import std_init, curses_init, colorama_init
from textprint.input import InputLineUpdater
from textprint.section import Section
from textprint.textprinter import TextPrinter

title_bar_section = Section(1)
console_section = Section(None, fake_line=(Color.BLUE >> "~"))
input_section = Section(1)
printer = TextPrinter([input_section, console_section, title_bar_section])
printer.update_dimensions()

input_line = input_section.println(printer, "")
title_bar = title_bar_section.println(printer, "Holder")
# we don't need a line for console_section because that's where we create a bunch of lines


def run_program(win):
    load_width = printer.dimensions[1] - 2
    std_init(win)
    curses_init()
    colorama_init()
    input_updater = InputLineUpdater(printer, input_line, win)

    title_bar_section.update_lines(printer)
    console_section.update_lines(printer)
    input_section.update_lines(printer, flush=True)

    input_section.goto(printer, 0, 0)
    number_count = 500
    for i in range(0, number_count + 1):
        # debug.update_lines(printer)
        # section loading bar
        way_there = floor(i / number_count * load_width)
        text = Color.BOLD + Color.BACK_RED + Color.CYAN + "["
        for j in range(0, load_width):
            if j < way_there:
                text += "#"
            else:
                text += " "
        text += "]"
        title_bar.contents = text
        title_bar.update(printer)
        # end section loading bar
        console_section.println(printer, "Hello there: {}".format(i))
        console_section.update_lines(printer)
        title_bar.update(printer)

        input_updater.update()  # this method also flushes the output
        # sleep(.02)
        if input_updater.should_exit:
            break
    while True:  # keep the program going
        if input_updater.should_exit:
            break


if __name__ == '__main__':
    wrapper(run_program)
