from typing import TYPE_CHECKING

from colorama.ansi import clear_line

if TYPE_CHECKING:
    from textprint.section import Section
    from textprint.textprinter import TextPrinter


class Line:
    """
    A class that holds data for a line. Should be created by a Section
    """
    # TODO add a color option
    def __init__(self, contents: str, section: 'Section', line_number: int):
        """

        :param contents: The contents of the line -> What text you want to be displayed on a line.
        :param section: The section that this line is in
        :param line_number: The line number given by section with the lowest value being 0. If a line for whatever \
                reason is deleted, the Section handling the lines should change the value accordingly. Note this is \
                relative to the section, not the whole TextPrinter
        """
        self.contents = contents
        self.section = section
        self.line_number = line_number

    def _do_goto(self, text_printer: 'TextPrinter', flush: bool = False):
        rows = len(self.section.lines) - self.line_number - 1
        columns = 0
        self.section.goto(text_printer, rows, columns, flush=flush)

    def update(self, text_printer: 'TextPrinter', flush: bool = False):
        """
        Takes no arguments because it updates the line based on the state of this Line
        :return: None
        """
        self._do_goto(text_printer, flush=False)
        columns = text_printer.get_rows_columns()[1]
        show = self.contents[:columns]  # TODO somehow get it to go onto the next line without glitching and fix colors
        # show = self.contents
        print(clear_line() + show, end="", flush=flush)

    def get_rows_taken(self):
        """
        Usually returns 1 but in the case that the line goes to the next line, it should return 2, or 3, etc.
        Should return the same amount whether or not update has been called first
        :return: The number of rows that this line is taken, usually 1
        """
        return 1
