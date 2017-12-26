import sys
import time
import warnings
from threading import Thread
from typing import List, TYPE_CHECKING, Tuple, Optional

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

if TYPE_CHECKING:
    from textadventure.input.inputhandling import InputObject


# deprecated
class StreamOutput(Thread, PlayerOutput):  # extending thread so we can let messages pile up and print them out easily

    """
    Deprecated because it's not updated (it doesn't use MessageParts) and the code is very ugly and unreadable

    This class is a PlayerOutput class that outputs the console by default or another stream if chosen.
    The run method along with the while True loop and everything inside it is pretty much just thrown together\
        with a lot of painful if statements. Of course, if you stare at it long enough, you might be convinced that you\
        have it down. However, there could be side effects of using different things and hopefully this is the only \
        class that has side effects related to the printing of text. Good luck future readers.

    This class is a basic example of printing the the console but the code required to print the messages it a lot\
    so the class will still be functional except it will not be used by default because using curses is awesome.
    """

    def __init__(self, stream=sys.stdout, is_unix=True):
        warnings.warn("You are using the StreamOutput class which is deprecated and not updated.")
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

                    names = []
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
        """The current Line object used by __print_parts"""

        self.messages = []
        """Used by __add_messages to add the parts to message_parts"""

        self.message_parts = [[]]  # type List[List[MessagePart]]
        """This is a list of lists of MessageParts where each list inside the list is a line."""
        self.current_line_parts = None  # type Optional[Tuple[List[MessagePart], int]]
        """[0] represents the MessageParts that should be on one line. [1] represents the time they started printing"""

        self.is_instant = False  # set to True when you want the update method to immediately print current message
        """A boolean that is True when you want the update method to immediately print current message. This\
            should only be used on the current message and if you want to print all the messages immediately, \
            call the update method and set immediate to True"""
        self._last_blank = 0
        """Used in on_input to tell how long it's been since the user pressed enter with no input"""

        self.wait_multiplier = 1

    def send_message(self, message: Message):
        # self.section.print(self.printer, str(["({},{},{}".format(part.print_before, part.main_text, part.print_after)
        #                                       for part in message.create_parts()]), flush=True)
        self.messages.append(message)

    def on_input(self, handler: 'Handler', player: 'Player', player_input: 'InputObject'):
        if player_input.is_empty():
            now = time.time()
            # if self._last_blank + 1 > now:
            self.__print_parts(immediate=True)  # only thing in if statement
            self._last_blank = now
            return True
        current_is_instant = self.is_instant

        self.send_message(Message(Color.YELLOW >> player_input.string_input, message_type=MessageType.IMMEDIATE))
        # self.send_message(Message(str([part.main_text for part in self.current_line_parts[0]])))
        self.is_instant = True  # we have regular so all the stuff before it should print immediately
        self.__add_messages()  # add the current message we just printed
        self.__print_parts(immediate=True)  # by default, this will change self.is_instant
        self.is_instant = current_is_instant  # reset is_instant to what is was before
        return False

    def on_action(self, handler: 'Handler', action: Action):
        pass

    def update(self, handler: 'Handler'):
        """If you're reading this, all you have to know is that this calls __add_messages and __print_parts"""
        self.__add_messages()
        self.__print_parts()

    def __add_messages(self):
        if len(self.message_parts) == 0:
            self.message_parts.append([])
        while len(self.messages) != 0:
            # print(Cursor.POS(0, 0) + str(time.time()) + "outputs.py", end="")
            """The above line that was commented out was used to check if this piece of code really is slow, however\
            This code executes in a fine amount of time."""
            current_messages = self.messages
            self.messages = []  # doing this makes this method mostly thread safe if we decide to change it later
            for message in current_messages:
                # self.section.print(self.printer, message.text, flush=True)
                # continue
                parts = message.create_parts()
                # since we called message.create_parts, we can change them if we would like

                for part in parts:
                    new_lines = 0
                    while '\n' in part.print_after:  # check how many new lines we want
                        new_lines += 1
                        part.print_after = part.print_after.replace("\n", "")

                    self.message_parts[len(self.message_parts) - 1].append(part)  # append a part to the last list
                    for i in range(0, new_lines):
                        self.message_parts.append([])

    def __print_parts(self, immediate=False):
        """
        :param immediate: Used throughout this method to tell if everything should be immediate
        """
        def iterate_parts():  # called below. This was turned into a method because we need to be able to return
            """Returns True at[0] if all of the parts were printed. And returns contents of line at [1]"""
            add_time = not self.is_instant and not immediate  # used to tell if we should add time to time_count

            parts = self.current_line_parts[0]  # type List[MessagePart]

            passed = now - self.current_line_parts[1]  # since we recalculate the amount of chars each time this\
            #       is called, we need to know how much time it has taken so far
            time_count = 0  # incremented for each character that has a wait_between another
            contents = ""  # the contents that we will return based on parts
            for part in parts:
                if add_time and time_count >= passed:  # first check if this message is instant then check time
                    return False, contents  # we are done printing. Must have been added from wait_after_print
                contents += part.print_before
                wait = part.wait_between * self.wait_multiplier
                if wait == 0:
                    contents += part.main_text
                else:
                    for c in part.main_text:
                        if add_time and time_count >= passed:
                            return False, contents  # we are done printing for now
                        contents += c
                        if add_time:
                            time_count += wait

                contents += part.print_after
                if add_time:
                    time_count += part.wait_after_print * self.wait_multiplier

            self.is_instant = False  # This makes it per line since normally, when this returns, it's the end of line
            return True, contents

        now = time.time()
        while True:  # we will return if we need to wait or if there's nothing left to do
            if self.current_line_parts is None:
                if len(self.message_parts) == 0:
                    return
                first_list = self.message_parts[0]
                if len(first_list) == 0:  # we don't want to create a line for no MessageParts if no comment> extra line
                    return
                self.message_parts.remove(first_list)
                self.current_line_parts = (first_list, time.time())
                self.current_line = self.section.print(self.printer, "")
            result = iterate_parts()  # this is where we call iterate_parts
            self.current_line.contents = result[1]
            self.current_line.update(self.printer)  # don't flush because whatever's controlling input will
            if not result[0]:
                # assert not immediate, "This shouldn't happen"
                return  # return if we still need to print more from the current parts (Later, not now)
            else:
                self.current_line_parts = None  # we're done printing all available parts


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
        self.printer.set_title("Trail of Ninjas - " + str(location))
