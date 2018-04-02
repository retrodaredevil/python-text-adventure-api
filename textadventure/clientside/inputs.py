import _thread
import sys
import threading
from threading import Thread
from typing import Optional

from textadventure.action import Action
from textadventure.handler import Handler
from textadventure.manager import Manager
from textadventure.sending.commandsender import InputGetter, OutputSender, OutputSenderType
from textprint.input import InputLineUpdater


class KeyboardInputGetter(InputGetter, Thread):
    DEFAULT_INPUT_PROMPT = ""  # because it doesn't look how we want it to

    def __init__(self, output: Optional[OutputSender] = None):
        """
        Note thread does not start itself

        :param output: The output to send raw messages to using ansi escapes or None if the console does not support
                       these or if these are unwanted
        """
        super().__init__()
        self.inputs = []
        self.output = output
        self.input_prompt = self.__class__.DEFAULT_INPUT_PROMPT

        self.daemon = True

    def run(self):
        while True:
            try:
                inp = input(self.input_prompt)
            except EOFError:
                _thread.interrupt_main()  # TODO find a better replacement
                # threading.main_thread().idk
                return

            self.input_prompt = self.__class__.DEFAULT_INPUT_PROMPT
            # if not self.should_use_input(inp):  # ignore blank lines
            #     if self.output is not None and self.output.get_sender_type() == OutputSenderType.CLIENT_UNIX_STREAM:
            #         # get rid of enter # back to prev: \033[F
            #         self.output.send_raw_message("\033[K\033[u\033[1A")  # gosh, it was worth trying lots of stuff
            #         # K: clear line, u: restore position, 1A: Move up 1 line   # ^ it works!!
            #         self.output.send_raw_flush()
            #
            #         self.output.print_immediately()
            #     continue

            self.inputs.append(inp)

    @staticmethod
    def should_use_input(inp: str):
        return len(inp) != 0 and not inp.isspace()

    def take_input(self):
        r = None
        if len(self.inputs) > 0:
            r = self.inputs[0]
            self.inputs.remove(r)

        return r


class BasicInputGetter(InputGetter, Manager):
    def __init__(self):
        pass

    def take_input(self):
        return input()

    def update(self, handler: 'Handler'):
        pass

    def on_action(self, handler: 'Handler', action: Action):
        pass


class TextPrinterInputGetter(InputGetter, Manager):
    """
    Note that you should also probably add an instance of InputLineUpdaterManager to the list of managers in \
        the Handler to show smoother input
    """
    def __init__(self, updater: InputLineUpdater):
        """
        Creates a TextPrinterInput which wraps a InputLineUpdater and implements the PlayerInput class to provide\
            ease to getting input even though you will have to create the InputLineUpdater yourself

        :param updater: The InputLineUpdater that input will be taken from
        """
        self.updater = updater
        self._amount_taken = 0

    def take_input(self):
        # self.updater.line_object.update(self.updater.text_printer)
        # self.updater.goto_cursor(flush=True)

        lines = self.updater.string_lines()
        if self._amount_taken < len(lines):
            r = lines[self._amount_taken]
            self._amount_taken += 1
            return r

        return None

    def update(self, handler: 'Handler'):
        # start = time.time()  # tested and seems to have a good speed
        self.updater.update()
        if self.updater.should_exit:
            raise KeyboardInterrupt("It seems updater.should_exit is True. Exiting program.")

    def on_action(self, handler: 'Handler', action: Action):
        pass
