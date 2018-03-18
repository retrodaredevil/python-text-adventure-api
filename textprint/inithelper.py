from typing import Callable

import sys


def curses_init():
    """
    This function imports curses and calls methods necessary for input
    """
    import curses
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.raw()  # allows us to receive keyboard interrupts
    curses.cbreak()


def curses_end():
    """
    If you aren't wrapping a function using curses.wrapper, you will have to call this whenever your program terminates
    """
    import curses
    curses.echo()
    curses.noraw()
    curses.nocbreak()
    curses.endwin()


def add_interrupt_handler(func: Callable):
    import signal

    def signal_handler(sig, frame):
        func()
        # raise KeyboardInterrupt("We have detected CTRL+C")
    signal.signal(signal.SIGINT, signal_handler)


def std_init(stdscr):
    """
    Should be called in order to be able to use the terminal in full screen

    Since the things called in here is only WindowObject specific, we don't need to reset it since it won't carry\
    over after we exit the program

    :param stdscr: The WindowObject returned from curses.initscr()
    """
    stdscr.clear()
    stdscr.keypad(True)  # allows constants from curses.<KEY_NAME> (ascii values above 255)
    stdscr.nodelay(True)  # stops all getch from the curses library from pausing the current Thread


def colorama_init():
    """
    If your program is compatible with a dos terminal, you may want to call this

    This tries to import colorama and initialize it. If it was unable, it will print to stderr but will not throw error
    """
    try:
        import colorama
        colorama.init()  # this should do things automatically
        # sys.stdout = colorama.AnsiToWin32(sys.stdout).stream it should do this automatically
    except ImportError:
        colorama = None
        print("Unable to import colorama", file=sys.stderr)
