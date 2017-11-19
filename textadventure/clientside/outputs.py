import sys
import time
import warnings
from threading import Thread
from typing import List

from textadventure.message import PlayerOutput, Message, MessageType
from textadventure.utils import join_list
from textprint.section import Section
from textprint.textprinter import TextPrinter


class StreamOutput(Thread, PlayerOutput):  # extending thread so we can let messages pile up and print them out easily

    """
    This class is a PlayerOutput class that outputs the console by default or another stream if chosen.
    The run method along with the while True loop and everything inside it is pretty much just thrown together\
        with a lot of painful if statements. Of course, if you stare at it long enough, you might be convinced that you\
        have it down. However, there could be side effects of using different things and hopefully this is the only \
        class that has side effects related to the printing of text. Good luck future readers.

    This class is a basic example of printing the the console but the code required to print the messages it a lot\
        so the class will still be functional except it will not be used by default because using curses is awesome
    """

    def __init__(self, stream=sys.stdout, is_unix=True):
        super().__init__()
        self.stream = stream
        self.is_unix = is_unix

        self.messages = []
        self.current_messages = []
        self.wait_multiplier = 1
        self.print_immediate = False  # if True, will be set back to False after done printing current_messages

        self.start()

    def send_message(self, message: Message):
        if message is None:
            raise Exception("Cannot add an Message that's None")
        if type(message) is not Message:
            raise Exception("Must be a message")
        self.messages.append(message)  # note that this may cause an issue if it gets reset right after (very unlikely)

    def run(self):
        from colorama import init, AnsiToWin32
        if not self.is_unix:
            init(autoreset=True)
            self.stream = AnsiToWin32(self.stream).stream  # change the stream to one that automatically converts it
        while True:
            if len(self.messages) > 0:
                self.current_messages = self.messages  # no need to clone because we will be resetting self.messages
                self.messages = []
                self.print_immediate = False
                for message in self.current_messages:
                    before_multiplier = 1  # used to make wait messages shorter
                    if self.print_immediate:
                        before_multiplier = 0.3
                    time.sleep(message.wait_in_seconds * before_multiplier)
                    to_print = message.text + message.ending  # TODO readd before

                    names: List[str] = []  # noinspection PyTypeChecker
                    for named in message.named_variables:
                        if isinstance(named, List):
                            names.append(join_list(list(map(str, named))))
                            # if you're wonder what the heck the above thing does, don't worry about it. But since you\
                            # asked, list(map(str, named)) transforms the list, named, into a list of strings, then\
                            # it calls join_list which there is some excellent documentation on that elsewhere. Good day
                        else:
                            names.append(str(named))  # named could be a string or something that has an __str__ method

                    try:
                        to_print = to_print.format(*names)  # tuple is needed or it ends up ['Bob']
                    except IndexError:
                        warnings.warn("Couldn't format to_print: '{}' with names: len:{}, values:{}.".format(
                            to_print, len(names), names))
                        warnings.warn("named_variables: len: {}, values: {}".format(len(message.named_variables),
                                                                                    message.named_variables))
                        continue
                    is_immediate = False  # only used with MessageType.TYPED used for |text| blocks to print immediately
                    # ^ not affected by Message properties, read code in for loop to understand
                    for c in to_print:
                        to_wait = 0  # in seconds # the smaller the faster
                        if not self.print_immediate:
                            if message.message_type == MessageType.TYPED:
                                to_wait = 0.018
                                if c == '|':  # allows a part of the message to be immediate but not all of the message
                                    is_immediate = not is_immediate

                                if is_immediate:
                                    to_wait = 0
                                elif c == '.':
                                    to_wait = 0.05
                                elif c == ' ':
                                    to_wait = 0.03
                                elif not str(c).islower():
                                    to_wait = 0.05
                            elif message.message_type == MessageType.TYPE_SLOW:
                                to_wait = 0.15

                        to_wait *= self.wait_multiplier

                        time.sleep(to_wait)  # this is where the wait is applied
                        if c != '|':  # don't print these characters
                            self.stream.write(c)  # print character
                            if self.is_unix:  # if it's windows, this will look terrible
                                self.stream.write("\033[s")  # save position for KeyboardInput
                        if message.message_type != MessageType.IMMEDIATE \
                                and (message.message_type != MessageType.TYPED or to_wait != 0) and not is_immediate:
                            self.stream.flush()  # flush the stream assuming that we need to
                    self.stream.flush()


class TextPrinterOutput(PlayerOutput):
    def __init__(self, printer: TextPrinter, section: Section):
        super().__init__()
        self.printer = printer
        self.section = section

    def send_message(self, message: Message):
        parts = message.create_parts()
        pass  # TODO TextPrinterOutput send_message not created
