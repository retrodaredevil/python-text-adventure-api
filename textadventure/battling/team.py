from typing import List

from textadventure.entity import Entity
from textadventure.utils import join_list


class Team:
    """
    A Team object has a list of entities that are on the team and a name to go along with the team.
    This does not import or do anything with Targets
    """
    def __init__(self, members: List[Entity], name: str = None):
        """
        A team can have one or more entities on it.
        @param members: The list of entities on this team (Can have any number of members)
        @param name: The name of the team. If None, it will become: Name1, Name2, Name3 and Name4
        """
        length = len(self.members)
        assert length > 0, "The members of a team cannot be 0."
        self.members = members
        if name is None:  # basically a default name
            name = join_list(list(map(str, self.members)))
        self.name = name

    def __str__(self):
        return self.name

    def __contains__(self, item):
        return item in self.members
