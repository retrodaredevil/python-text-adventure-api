import os
import sys
from typing import List, Optional

from textprint.colors import CSI
from textprint.section import Section


class TextPrinter:
    """
    This class is used to clear the whole screen and write to it using sections to make a awesome looking text \
        interface using curses
    """
    def __init__(self, sections: List[Section], output=sys.stdout, print_from_top=False, stdscr=None):
        """
        Creates a TextPrinter object that will be used by the Sections

        :param sections: The list of sections where the section at index 0 will be at the bottom. Ex: Most of the time\
                you will have your input_section at the bottom. Note that there can only be one Section where\
                Section#rows is None and Section#fill_up_left_over is True. If there are multiple with that, then two \
                sections will conflict with each other and you will get a recursion error.
        :param output: The output to write to. Defaults to sys.stdout and if you change it, you must make sure that\
                other libraries like curses that are being used are altered correctly
        :param print_from_top: Normally False. If True, text will print from the top and the order of the sections\
                will be flipped (Every line seen will be flipped
        """
        self.sections = sections
        self.output = output
        self.print_from_top = print_from_top
        self.stdscr = stdscr
        """If you are using curses (very likely) You should pass the WindowObject created with initscr."""

        self.dimensions = (80, 24)
        """[0] is rows [1] is columns"""
        self._title = None

        # self.default_position: Optional[Tuple[int, int]] = (0, 0)  # Optional Tuple where [0] is rows and [1] is col
        self._known_goto_position = None
        """Used by the goto and print methods. When None, it means that we are not sure of the specific location\
                of the cursor meaning that goto should print. If not None, [0] represents rows and [1] represents\
                columns. (y, x) The goto method should check this if it is not None. Also note that since [0] is used\
                by goto, it doesn't represent the value of 'row' passed to goto, instead it represents the value\
                printed to the console."""

    def update_all_lines(self, flush=True):
        """
        A simple method used to update all lines. Note that normally, this shouldn't be called at all unless you \
        REALLY need to reset the screen.

        :param flush: True if you want to flush the stream. This is True by default unlike most other methods
        """
        for section in self.sections:
            section.update_lines(self, flush=False, force_reprint=True)

        if flush:
            self.flush()

    def calculate_lines_to(self, section: Optional[Section]) -> int:
        """
        Calculates the number of lines until the section (Not including the passed section)

        :param section: The section to get the number of lines to. If None, it will get the lines taken from all
        :return: The number of lines until this section
        """
        lines = 0
        for s in self.sections:
            if s == section:
                return lines
            # assert s != section, "I don't even know why this would happen"
            lines += s.get_lines_taken(self)
        if section is not None:
            assert section not in self.sections, "We went through all of them, it should not be in there"
            raise ValueError("The passed section needs to be in self.sections")
        return lines

    def calculate_lines_after(self, section: Section) -> int:
        """
        Calculates the number of lines after a section (Not including the passed section)

        :param section: The section that you want to get the number of lines after
        :return: The number of lines after the passed section
        """
        lines = 0
        adding = False
        for s in self.sections:
            if adding:
                # assert section != s, "This should not happen in calculate_lines_after", really we shouldn't need this
                lines += s.get_lines_taken(self)
            elif s == section:
                adding = True

        if adding is False:
            assert section not in self.sections, "We went through all of them, it should not be in there."
            raise ValueError("The passed section needs to be in self.sections")
        return lines

    def goto(self, row: int, column: int, flush=False):
        """
        A simple method that goes to the specified coordinates where 0, 0 is the bottom right

        :param row: The row. Note that if 0, it will not be in the upper part of the screen, instead at the very bottom
        :param column: The column
        :param flush: True if you want to flush. By default False.
        :return: None
        """
        # print("\033[{};{}H".format(int(window_rows) - row, column), end="")
        position = self._known_goto_position
        used_rows = self.dimensions[0] - row if not self.print_from_top else row + 1
        if position is not None and position[0] == used_rows and position[1] == column:
            # notice that this if statement uses used_rows and not rows. Please take note when debugging
            return
        # self.print(self.__cursor.POS(column, used_rows), end="", flush=flush)
        self.print(CSI + str(used_rows) + ";" + str(column) + "H", end="", flush=flush)
        self._known_goto_position = used_rows, column  # use used_rows so if resize, if statement above won't fire
        # print("goto {}".format(self._known_goto_position), file=sys.stderr)

    def print(self, text="", flush=False, end=""):
        """
        Allows you to print text to self.output. Normally, you would use unix escapes since that what this library \
        uses. Normally, you shouldn't call this method because you should let lines handle this

        :param text: The text you want to print
        :param flush: Do you want to flush it?
        :param end: The ending, by default and normally an empty string. Since this library handles multiple lines\
                with Line objects, normally you wouldn't and shouldn't change this.
        """
        # print(text, flush=flush, end=end)
        to_write = text + end
        if to_write:  # check if the string isn't empty. If it isn't, actually do something
            # print("value: {}".format([text]), file=sys.stderr)
            self.output.write(to_write)
            self._known_goto_position = None
        if flush:
            # print("flush {}".format(time.time()), file=sys.stderr)
            self.output.flush()

    def flush(self):
        self.print(flush=True)

    def set_title(self, title: str, flush=False, reprint=False):
        """
        Sets the title of the terminal window

        :param title: The string title that you want to set the title of the terminal window to
        :param flush: By default False. Set to True if you want to flush the stream
        :param reprint: By default False. If True, ignores the last call to set_title. When False, this checks to see\
                if the last passed title is the same as the current passed title. If it is, it won't print anything.
        :return: The escaped string that was printed to self.output or None if reprint is True and the last passed \
                string is the same. This doesn't serve much of a purpose unless you want to know if it is None
        """
        # I made getter and setter methods because you need to be able to pass default parameters and I feel that\
        #   getters and setters emphasize that something is being done (printing)

        # used https://stackoverflow.com/questions/2330393/how-to-set-the-program-title-in-python
        # TODO This won't work on windows. Need to call import os; os.system(title)
        r = None
        if reprint or self.get_title() != title:
            r = "\x1b]2;" + title + "\x07"
            self.print(r, flush=flush)
            self._title = title

        return r

    def get_title(self):
        """
        Gets the string passed to last set_title call or None if set_title hasn't been called or the title isn't known
        :return: Returns the current known title or None if set_title hasn't been called before
        """
        return self._title

    def update_dimensions(self):
        """
        Updates self.dimensions.
        Note that calling this repeatedly will slow down your program A LOT
        """
        if self.stdscr is not None:
            irows, icolumns = self.stdscr.getmaxyx()
        else:
            rows, columns = os.popen('stty size', 'r').read().split()
            irows = int(rows)
            icolumns = int(columns)
            if irows == 0:
                irows = 80
            if icolumns == 0:
                icolumns = None

        self.dimensions = (irows, icolumns)
