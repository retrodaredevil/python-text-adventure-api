from typing import Optional, List, TYPE_CHECKING, Tuple

from textprint.line import Line

if TYPE_CHECKING:
    from textprint.textprinter import TextPrinter


class Section:
    def __init__(self, rows: Optional[int], columns: Optional[int] = None,
                 force_rows: bool = True):
        """
        :param rows: The max number of rows to show, or None to show len(self.lines)
        :param columns: The max number of columns, unused for right now
        :param force_rows: By default True. When True and rows is not None, when the amount of rows printed is less \
                than rows, this will still fill up the amount of rows determined by parameter rows. If False, this \
                section will not be the max number of rows (rows) until this has printed enough.
        """
        super().__init__()  # for multiple inheritance
        self.rows = rows
        self.columns = columns
        self.force_rows = force_rows

        self.lines: List[Line] = []  # noinspection PyTypeChecker

    def get_lines_taken(self, printer: 'TextPrinter', include_extra_rows=True):
        length = len(self.lines)
        if include_extra_rows:
            for line in self.lines:
                length += line.get_rows_taken()  # could be 2 or 3 if the line is overflowing
        if self.rows is not None:
            if self.force_rows or length > self.rows:
                return self.rows  # this is very likely to be returned
            return length
        # now this code will only be run if self.rows is None
        before = printer.calculate_lines_to(self)
        after = printer.calculate_lines_after(self)
        else_height = (before + after)
        # isn't recursive because it doesn't call the get_lines_taken method from the passed section (self)
        height = printer.get_rows_in_current_window()
        if else_height + length >= height or self.force_rows:  # if length will put other things off screen or full
            length = height - else_height  # will set the exact amount needed to show everything on screen (by hiding\
            #       lines)

        return length

    def goto(self, text_printer: 'TextPrinter', row: int, column: int, flush: bool = False) -> Tuple[int, int]:
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

    def print(self, text_printer: 'TextPrinter', message: str, flush: bool = False) -> Line:
        line = Line(message, self, len(self.lines))
        self.lines.append(line)
        self.update_lines(text_printer, flush=flush)  # write to the line that the newly created Line should occupy,\
        #       if a new line was needed, it should have been added
        return line

    def update_lines(self, text_printer: 'TextPrinter', flush: bool = False):
        taken = self.get_lines_taken(text_printer)
        row = 0
        for line in self.lines:
            if len(self.lines) - row <= taken:
                line.update(text_printer, flush=flush)
            row += line.get_rows_taken()  # TODO if the Section#row is only 1 and it overflows, it will glitch

        for i in range(row - taken, 0):
            # this was very painful to think about, basically, it creates a fake line for each empty line that is \
            #       owned by the section and that is not an actual line that has already been printed.
            # notice that we go to zero. This is because the first line's line_number is 0. Yes, it's weird but it works
            fake_line = Line("", self, i)
            fake_line.update(text_printer)
