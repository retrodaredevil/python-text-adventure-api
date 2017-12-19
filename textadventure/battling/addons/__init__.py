"""
The packages in here should either be original packages that wouldn't make sense to not use the battle api, or\
packages that import from textadventure.addons where the contents of the package inside textadventure.battling.addons\
imports from the corresponding package in textadventure.addons and provides additional features that are only \
specific to the battle api

Normally, each package should implement a Savable in one of their classes since most of what addons are meant for are\
adding extra data and extra content affected by that data
"""