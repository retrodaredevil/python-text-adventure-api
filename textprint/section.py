from typing import Optional, List, TYPE_CHECKING, Tuple

from textprint.line import Line

if TYPE_CHECKING:
    from textprint.textprinter import TextPrinter


class Section:
    def __init__(self, rows: Optional[int], columns: Optional[int] = None,
                 force_rows: bool = True, fake_line: Optional[str] = None):
        """
        :param rows: The max number of rows to show, or None to show len(self.lines)
        :param columns: The max number of columns, unused for right now
        :param force_rows: By default True. When True and rows is not None, when the amount of rows printed is less \
                than rows, this will still fill up the amount of rows determined by parameter rows. If False, this \
                section will not be the max number of rows (rows) until this has printed enough.
        :param fake_line: A string that is only used if force_rows is True, if None, fake_lines aren't used, otherwise\
                fake_lines are placed in all the lines that the section occupies except for the ones that have already\
                been printed.
        """
        super().__init__()  # for multiple inheritance
        self.rows = rows
        self.columns = columns
        self.force_rows = force_rows
        self.fake_line = fake_line

        self.lines: List[Line] = []  # noinspection PyTypeChecker

    def get_lines_taken(self, printer: 'TextPrinter', include_extra_rows=True):
        terminal_width = printer.dimensions[1]
        length = len(self.lines)
        if include_extra_rows:  # most of the time, this is True
            length = 0
            for line in self.lines:
                length += line.get_rows_taken(terminal_width)  # could be 2 or 3 if the line is overflowing
        if self.rows is None:  # is there no set number of rows?
            if not self.force_rows:  # if we aren't forcing the number of rows this section has
                return length  # Now then, we'll just use as many rows as we'd like

            before = printer.calculate_lines_to(self)
            after = printer.calculate_lines_after(self)
            else_height = (before + after)
            # isn't recursive because it doesn't call the get_lines_taken method from the passed section (self)
            height = printer.dimensions[0]
            if else_height + length >= height or self.force_rows:  # if length will put other things off screen or full
                length = height - else_height  # will set the exact amount needed to show everything on screen (by \
                #       hiding lines)
            return length

        # self.rows is not None
        if self.force_rows or length > self.rows:
            return self.rows  # this is very likely to be returned
        return length

    def goto(self, text_printer: 'TextPrinter', row: int, column: int, flush=False) -> Tuple[int, int]:
        """
        Changes the cursor to the position relative to this section

        :param text_printer: The TextPrinter that this section is contained in
        :param row: The row relative to this section. (0 will be the first line which usually displays the last \
                element in self.lines)
        :param column: The column, nothing special here unless this is changed in the future. Usually you'd set it \
                to 0 unless you want to start printing in the middle of the screen.
        :param flush: Normally False unless you are calling this method and nothing else. If this is False and you\
                don't have another method flush (or yourself), the console will not show the cursor in the wanted \
                position
        :return: A Tuple value where [0] represents the row and [1] represents column (y, x) (yes weird but [0] is \
                more important) Note that the reason this is returned is because row will likely be different than \
                the passed row because this method acts relative to this section. (The returned value is not)
        """
        r = row + text_printer.calculate_lines_to(self)
        c = column
        text_printer.goto(r, c, flush=flush)

        return r, c

    def print(self, text_printer: 'TextPrinter', message: str, flush=False) -> Line:
        line = Line(message, self, len(self.lines))
        self.lines.append(line)

        # we will need force_reprint, because we need to redraw all lines in correct places
        self.update_lines(text_printer, flush=flush, force_reprint=True)
        # write to the line that the newly created Line should occupy,\
        #       if a new line was needed, it should have been added
        return line

    def __remove_old_lines(self):
        if len(self.lines) < 110:  # we should remove 10 lines at a time -> might improve performance
            return
        amount_removed = 0
        while len(self.lines) > 100:
            del self.lines[0]  # removes first item by index
            amount_removed += 1

        for line in self.lines:
            line.line_number -= amount_removed

    def update_lines(self, text_printer: 'TextPrinter', flush=False, force_reprint=False):
        """
        Simple method to update all the lines and make sure they are in the right place

        :param text_printer: The TextPrinter that contains this section
        :param flush: By default False. Determines whether the stream will be flushed at the end of this method call
        :param force_reprint: By default False
        :return:
        """
        self.__remove_old_lines()
        terminal_width = text_printer.dimensions[1]

        # length = len(self.lines)
        length = 0  # calculate length with this for loop
        for line in self.lines:
            length += line.get_rows_taken(terminal_width)

        taken = self.get_lines_taken(text_printer)  # how many lines should this section take
        row = 0  # the current row usually incremented by 1 or 2 if a line overflows
        for line in self.lines:  # update all the lines that should be on screen
            if length - row <= taken:
                line.update(text_printer, reprint=force_reprint)
            row += line.get_rows_taken(terminal_width)
        assert row == length, "Since this is False, then one of the Line#update isn't doing something right."

        if self.fake_line is not None:
            # adding extra lines may look like it affected the speed, but it's because it happens even with regular \
            #       lines when the screen fills up.
            extra_lines = length - len(self.lines)
            # for line in self.lines:  used when extra_lines is initially 0
            #     extra_lines += line.get_rows_taken(terminal_width) - 1
            for i in range(row - taken, extra_lines * -1):
                # this was very painful to think about, basically, it creates a fake line for each empty line that is \
                #       owned by the section and that is not an actual line that has already been printed.
                # notice that we go to zero. This is because the first line's line_number is 0. (Goes negative to pos)
                fake_line = Line(self.fake_line, self, i)
                fake_line.update(text_printer)

        if flush:
            text_printer.flush()
