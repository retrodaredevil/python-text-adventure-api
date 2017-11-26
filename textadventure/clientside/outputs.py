import sys
import time
import warnings
from threading import Thread
from typing import List

from textadventure.action import Action
from textadventure.handler import Handler
from textadventure.manager import Manager
from textadventure.message import PlayerOutput, Message, MessageType, MessagePart
from textadventure.player import Player
from textadventure.utils import join_list
from textprint.colors import Color
from textprint.line import Line
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
        self.wait_multiplier = 1
        self.print_immediate = False  # if True, will be set back to False after done printing current_messages

        # already defined, stuff and starting this Thread
        self.daemon = True
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
                current_messages = self.messages  # no need to clone because we will be resetting self.messages
                self.messages = []
                self.print_immediate = False
                for message in current_messages:
                    before_multiplier = 1  # used to make wait messages shorter
                    if self.print_immediate:
                        before_multiplier = 0.3
                    time.sleep(message.wait_in_seconds * before_multiplier)
                    to_print = message.text + message.end

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


class TextPrinterOutput(Manager, PlayerOutput):
    def __init__(self, printer: TextPrinter, section: Section):
        """
        Creates a TextPrinterOutput but does not start the Thread
        """
        super().__init__()
        self.printer = printer
        self.section = section
        self.current_line = None

        self.messages = []

        self.message_number = 0

    def send_message(self, message: Message):
        # self.section.print(self.printer, str(["({},{},{}".format(part.print_before, part.main_text, part.print_after)
        #                                       for part in message.create_parts()]), flush=True)
        self.messages.append(message)

    def on_action(self, handler: 'Handler', action: Action):
        pass

    def update(self, handler: 'Handler'):
        # return
        while True:
            # self.input_line_updater.update_line()  # will be run after messages print and as often as possible
            if len(self.messages) == 0:
                break  # change to continue if this were a Thread
            current_messages = self.messages
            self.messages = []
            for message in current_messages:
                # self.section.print(self.printer, message.text, flush=True)
                # continue
                parts: List[MessagePart] = message.create_parts()  # noinspection PyTypeChecker
                for index, part in enumerate(parts):
                    # now since we are going to start using current_line, we should make sure it is initialized
                    if self.current_line is None:
                        # this will be fired if it hasn't been initialized before or there was a new line
                        self.current_line = self.section.print(self.printer, "", flush=True)  # debug: change to "(a)"
                    self.current_line.contents += part.print_before
                    if part.wait_between == 0:
                        self.current_line.contents += part.main_text
                    else:
                        for c in part.main_text:
                            assert c != '\n', "There shouldn't be any backslashes in part.main_text"
                            self.current_line.contents += c
                            self.current_line.update(self.printer, flush=True)  # flush it because we are about to sleep
                            time.sleep(part.wait_between)
                    new_lines = 0
                    after = part.print_after  # we don't want to change part.print_after
                    while '\n' in after:  # check how many new lines we want
                        new_lines += 1
                        after = after.replace("\n", "")
                    # now that we're out of the while loop and we know how many new lines we need, 'after' is not used
                    if len(after) != 0:
                        self.current_line.contents += after  # no new lines anymore, add after
                        self.current_line.update(self.printer)
                    for i in range(0, new_lines):  # right now, new_lines should only be 0 or 1, but prepare for future
                        # self.current_line = self.section.print(self.printer, "#:'{}',p:'{}'".format(self.message_number,
                        #                                                                             index))
                        if self.current_line is None:
                            # will happen if new_lines is > 1
                            self.section.print(self.printer, "")  # change "" to "(b)" for debugging
                        self.current_line.contents += ""  # change "" to "(c)" for debugging
                        self.current_line = None
                    # if new_lines != 0:  # update if we printed more lines in the for loop
                    #     self.current_line.update(self.printer)
                    # self.section.update_lines(self.printer, flush=True)  # this line makes it look bad
                    if part.wait_after_print != 0:
                        time.sleep(part.wait_after_print)

                self.message_number += 1


class LocationTitleBarManager(Manager):
    def __init__(self, player: Player, printer: TextPrinter, line: Line):
        self.player = player
        self.printer = printer
        self.line = line

    def on_action(self, handler: 'Handler', action: Action):
        pass

    def update(self, handler: 'Handler'):
        location = self.player.location
        point = location.point
        self.line.contents = Color.CYAN >> (Color.BOLD >> "{} at x: {}, y: {}, z: {}".format(location,
                                                                                             point.x, point.y, point.z))
        self.line.update(self.printer)  # don't flush it because it will put the cursor in a different spot
