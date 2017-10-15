from textadventure.command import SimpleCommandHandler


class StartFightCommandHandler(SimpleCommandHandler):

    command_names = []
    description = "Used to start a battle with an another entity."

    def __init__(self):
        super().__init__(self.__class__.command_names, self.__class__.description)

