from typing import Optional, List

from textprint.line import Line


class Section:
    def __init__(self, rows: Optional[int], columns: Optional[int] = None, force_rows: bool = True):
        """

        :param rows:
        :param columns:
        :param force_rows: By default True. When True and rows is not None, when the amount of rows printed is less \
                than rows, this will still fill up the amount of rows determined by parameter rows. If False, this \
                section will not be the max number of rows (rows) until this has printed enough.
        """
        self.rows = rows
        self.columns = columns

        self.lines: List[Line] = []
