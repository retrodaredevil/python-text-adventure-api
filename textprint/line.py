

class Line:
    """
    A class that holds data for a line. Should be created by a Section
    """
    # TODO add a color option
    def __init__(self, contents: str):
        """

        :param contents: The contents of the line -> What text you want to be displayed on a line.
        """
        self.contents = contents

    def update(self):
        """
        Takes no arguments because it updates the line based on the state of this Line
        :return: None
        """
        # TODO not working, I still have to think how I'm going to do this
