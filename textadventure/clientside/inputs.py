from threading import Thread

from textadventure.action import Action
from textadventure.clientside.outputs import StreamOutput
from textadventure.handler import Handler
from textadventure.manager import Manager
from textadventure.sending.commandsender import PlayerInputGetter
from textprint.input import InputLineUpdater


class KeyboardInputGetter(PlayerInputGetter, Thread):
    DEFAULT_INPUT_PROMPT = ""  # because it doesn't look how we want it to

    def __init__(self, stream_output: StreamOutput):
        """

        :param stream_output: The stream output or None if the PlayerOutput object isn't a StreamOutput
        """
        super().__init__()
        self.inputs = []
        self.stream_output = stream_output
        self.__input_prompt = self.__class__.DEFAULT_INPUT_PROMPT
        self.start()

    # def set_input_prompt(self, message: str):
    #     self.__input_prompt = message

    def run(self):
        while True:
            inp = str(input(self.__input_prompt))
            self.__input_prompt = self.__class__.DEFAULT_INPUT_PROMPT
            if not self.should_use_input(inp):  # ignore blank lines
                if self.stream_output is not None:
                    # get rid of enter # back to prev: \033[F
                    if self.stream_output.is_unix:
                        self.stream_output.stream.write("\033[K\033[u\033[1A")  # gosh, it was worth trying lots of stuf
                        self.stream_output.stream.flush()
                    # K: clear line, u: restore position, 1A: Move up 1 line   # ^ it works!!

                    '''
                    Can we just take a moment to appreciate whatever the heck I created does?
                    All ya gotta do it press enter and this little if statement makes it happen.
                    Duck this doesn't work on windows. I've been using gitbash. Duck DOS operating system wtf
                    '''

                    self.stream_output.print_immediate = True
                continue

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


class InputLineUpdaterManager(Manager):
    """
    Whenever the update method is called, updates self.updater using update_line.
    Using this class helps the input look cleaner since InputLineUpdater runs on another Thread
    """
    def __init__(self, updater: InputLineUpdater):
        self.updater = updater

    def on_action(self, handler: 'Handler', action: Action):
        pass

    def update(self, handler: 'Handler'):
        # start = time.time()  # tested and seems to have a good speed
        self.updater.update()
        if self.updater.should_exit:
            raise KeyboardInterrupt("It seems updater.should_exit is True. Exiting program.")
        # after = time.time()
        # taken = after - start
        # print(Cursor.POS(0, 0) + str(taken) + " seconds. inputs.py out", end="", flush=True)
        # time.sleep(1)


class TextPrinterInputGetter(PlayerInputGetter):
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
