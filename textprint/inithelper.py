

def std_init(stdscr):
    """
    Should be called in order to be able to use the terminal in full screen
    :param stdscr: The WindowObject returned from curses.initscr()
    """
    stdscr.clear()
    stdscr.keypad(True)  # allows constants from curses.<KEY_NAME> (ascii values above 255)
    stdscr.nodelay(True)  # stops all getch from the curses library from pausing the current Thread


def curses_init():
    """
    This function imports curses and calls methods necessary for input
    """
    import curses
    curses.use_default_colors()
    curses.noecho()
    curses.raw()  # allows us to receive keyboard interrupts
    curses.cbreak()


def colorama_init():
    """If your program is compatible with a dos terminal, you may want to call this"""
    import colorama
    colorama.init()
