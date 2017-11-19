import os
from typing import List, Optional

from colorama import init, Cursor
# from colorama.ansi import CSI

from textprint.section import Section


class TextPrinter:
    """
    This class is used to clear the whole screen and write to it using sections to make a awesome looking text \
        interface using curses
    """
    def __init__(self, sections: List[Section]):
        self.sections = sections
        self.__cursor = Cursor  # note that this isn't creating an object, it's an object already made

        # noinspection PyTypeChecker
        # self.default_position: Optional[Tuple[int, int]] = (0, 0)  # Optional Tuple where [0] is rows and [1] is col
        init()

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
                # assert section != s, "This should not happen in calculate_lines_after"
                lines += s.get_lines_taken(self)
            elif s == section:
                adding = True

        if adding is False:
            assert section not in self.sections, "We went through all of them, it should not be in there."
            raise ValueError("The passed section needs to be in self.sections")
        return lines

    def goto(self, row: int, column: int, flush: bool = False):
        """
        A simple method that goes to the specified coordinates where 0, 0 is the bottom right
        :param row: The row. Note that if 0, it will not be in the upper part of the screen, instead at the very bottom
        :param column: The column
        :param flush: True if you want to flush. By default False.
        :return: None
        """
        # print("\033[{};{}H".format(int(window_rows) - row, column), end="")
        print(self.__cursor.POS(column, self.get_rows_in_current_window() - row), end="", flush=flush)

    def get_rows_in_current_window(self):
        window_rows = os.popen("stty size", "r").read().split()[0]
        return int(window_rows)

    # def save_position(self):
    #     """
    #     :return: A solution that is meant to be simple to save where the mouse cursor is. You can retrieve it by \
    #             calling retrieve_position
    #     """
    #     print(CSI + "s", end="", flush=False)
    #
    # def retrieve_position(self):
    #     print(CSI + "u", end="", flush=True)
