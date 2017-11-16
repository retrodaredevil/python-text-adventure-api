import curses
import sys
from threading import Thread
from typing import List, TYPE_CHECKING

from textprint.line import Line


if TYPE_CHECKING:
    from textprint.textprinter import TextPrinter


class EditableLine:
    def __init__(self, contents: str):
        self._original = contents
        """The original string that should not be changed after the creation of the object."""
        self.before = contents
        """The text before the cursor"""
        self.after = ""
        """The text after the cursor"""

    def type(self, to_type: str):
        self.before += to_type

    def reset(self):
        self.before = self._original
        self.after = ""

    def delete(self, amount_delete_forward: int):
        if amount_delete_forward == 0:
            return
        elif amount_delete_forward < 0:  # backspace
            self.before = self.before[:amount_delete_forward]  # delete from back of string
        else:  # delete key
            self.after = self.after[amount_delete_forward:]

    def move(self, amount_forward: int):
        if amount_forward == 0:
            return
        elif amount_forward < 0:  # remove some character from before, add it to after (Going to the left)
            # amount_forward is negative but notice that we aren't multiplying amount_forward by -1 because we shouldn't
            before = self.before[: amount_forward]
            move = self.before[amount_forward:]
            self.after = move + self.after
            self.before = before
            return
        # now we will remove some character from after and add it to self.before (Going to the right)
        # amount_forward is positive
        after = self.after[amount_forward:]  # remove first character(s)
        move = self.after[:amount_forward]  # delete the whole string except for first char(s)
        self.before += move  # add the stuff removed from after to before
        self.after = after


class InputLineUpdater(Thread):
    """
    This class uses the curses library to get keyboard input before pressing enter.
    """
    def __init__(self, text_printer: 'TextPrinter', line: Line, win):
        """
        :param text_printer: The text TextPrinter object that this instance will be updating
        :param line: The line to display the user's input on
        :param win: the object created by curses.initscr()
        """
        super().__init__()
        self.text_printer = text_printer
        self.line_object = line
        self._win = win
        # noinspection PyTypeChecker
        # self.lines: List[str] = []  # once a string is appended, it should not be altered on this list
        # self._current_line = ""

        # noinspection PyTypeChecker
        self._editable_lines: List[EditableLine] = []
        self._current_line = EditableLine("")
        self._line_index = 0  # The line that should be gotten. 0 represents the most recent line

        self.should_exit = False  # is set to True when we receive a key combination that says to stop the program

        self.times_initialized = 0

    def current_line(self):
        if self._line_index == 0:
            return self._current_line
        return self._editable_lines[len(self._editable_lines) - self._line_index]  # if 1 get most recent printed line

    def _reset_editable_lines(self):
        for line in self._editable_lines:
            line.reset()

    def current_line_string(self):
        line = self.current_line()
        return line.before + line.after

    def do_update(self):
        self.line_object.contents = self.current_line_string()
        self.line_object.update(self.text_printer)
        self.goto_cursor(flush=True)  # now we will flush it

    def goto_cursor(self, flush=False):
        self.line_object.section.goto(self.text_printer, 0, len(self.current_line().before) + 1, flush=flush)

    def keypad_key(self, key, data=()):
        """
        Should be called for keys that aren't actual characters that should be shown. (Special characters and keycodes)
        :param key: A key normally one from curses.<KEY_NAME> because that's what the default implementation of \
                this function
        :param data: The data to go along with the keypress like how much to go. May be useful in the future \
                if you are able to call this function with something in place of data that makes sense, do so, \
                otherwise, data is not used in the default implementation
        :return:
        """
        if key == 10 or key == curses.KEY_ENTER:
            self._editable_lines.append(self._current_line)
            self._current_line = EditableLine("")
            self._reset_editable_lines()
        elif key == curses.KEY_BACKSPACE:
            self.current_line().delete(-1)
        elif key == curses.KEY_DC:
            self.current_line().delete(1)
        elif key == 4 or key == 3:
            self.should_exit = True
        elif key == curses.KEY_LEFT:
            self.current_line().move(-1)
        elif key == curses.KEY_RIGHT:
            self.current_line().move(1)
        else:
            self.current_line().type(str(curses.keyname(key)) + "int({})".format(key))

        self.do_update()

    def run(self):
        self._start_loop(self._win)

    def _start_loop(self, win):
        # thanks https://stackoverflow.com/a/40154005/5434860
        print("Initializing win using initscr. Initiation number: {} (Starts at 0)".format(self.times_initialized))
        self.times_initialized += 1
        win.clear()
        curses.noecho()
        win.keypad(True)  # allows constants from curses.<KEY_NAME>
        curses.raw()  # allows us to receive keyboard interrupts
        curses.cbreak()
        # now that we have that initialized, we can start listening in on stuff
        while True:
            if self.should_exit:
                break
            char_int = win.getch()
            character = chr(char_int)

            if char_int not in range(32, 127):
                self.keypad_key(char_int)
                continue  # we don't want to add a character that's not valid here

            # if we made it here, the character typed is a normal character
            self.current_line().type(character)
            self.do_update()
