import curses
import sys
from threading import Thread
from typing import List, TYPE_CHECKING

from textprint.line import Line


if TYPE_CHECKING:
    from textprint.textprinter import TextPrinter


class EditableLine:
    def __init__(self, contents: str):
        self.original = contents
        """The original string that should not be changed after the creation of the object. Should be used if you \
                want an accurate representation of what was there when the player pressed enter."""
        self.before = contents
        """The text before the cursor"""
        self.after = ""
        """The text after the cursor"""

    def type(self, to_type: str):
        self.before += to_type

    def reset(self):
        self.before = self.original
        self.after = ""

    def delete(self, amount_delete_forward: int):
        if amount_delete_forward == 0:
            return
        elif amount_delete_forward < 0:  # backspace
            self.before = self.before[:amount_delete_forward]  # delete from back of string
        else:  # delete key
            self.after = self.after[amount_delete_forward:]

    def home(self):
        """
        Moves the cursor to the beginning of the line
        """
        self.after = self.before + self.after
        self.before = ""

    def end(self):
        """
        Moves the cursor to the end fo the line.
        If all you need to do is reset the cursor position to the end of the line, this should do it.
        """
        self.before += self.after
        self.after = ""

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
        Creates an InputLineUpdater but does not start the thread. Note that it is recommended to set daemon to True
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
        self._current_line = EditableLine("")  # remember most of the time you should call current_line()
        """An EditableLine object that is used to keep track of what the player typed an the cursor position. When\
                the player presses enter, this resets and the object that was here before the enter pressed has \
                not been added to self._editable_lines but instead probably been destroyed by the GC"""
        self._line_index = 0  # The line that should be gotten. 0 represents the most recent line

        self.should_exit = False  # is set to True when we receive a key combination that says to stop the program

        self.times_initialized = 0

    def current_line(self):
        if self._line_index == 0:
            return self._current_line
        assert 0 <= self._line_index <= len(self._editable_lines), "_line_index isn't in range: {}".format(
            self._line_index)  # both <= because  we already checked if it is zero

        return self._editable_lines[len(self._editable_lines) - self._line_index]  # if 1 get most recent printed line

    def string_lines(self):
        return [line.original for line in self._editable_lines]

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
        """
        current = self.current_line()  # current line that may not actually be self._current_line
        if key == 10 or key == curses.KEY_ENTER:
            current.end()  # move the cursor to end
            self._editable_lines.append(EditableLine(current.before))  # create a new line and add it
            self._current_line = EditableLine("")  # even though current may not be this, we want to reset this
            self._line_index = 0  # set the line back to _current_line
            self._reset_editable_lines()  # reset all the EditableLines back to their original
        elif key == curses.KEY_BACKSPACE:
            current.delete(-1)
        elif key == curses.KEY_DC:
            current.delete(1)
        elif key == 4 or key == 3:
            self.should_exit = True  # for a developer who wants to make a clean exit of the program
        elif key == curses.KEY_LEFT:
            current.move(-1)
        elif key == curses.KEY_RIGHT:
            current.move(1)
        elif key == curses.KEY_UP or key == curses.KEY_DOWN:
            if key == curses.KEY_UP:
                self._line_index += 1  # remember when 0, current line will be self._current_line
            else:
                self._line_index -= 1
            self._line_index = max(0, min(self._line_index, len(self._editable_lines)))  # clamp
        elif key == curses.KEY_END:
            current.end()
        elif key == curses.KEY_HOME:
            current.home()
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
