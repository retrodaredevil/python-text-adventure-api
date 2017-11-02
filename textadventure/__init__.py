"""
This package should only have api related stuff in it. For an actual game, look at the game package
Also, this is a text adventure however, the word frame as the abstract meaning for each time the loop executes or each\
    frame

Methods with an _ in front of them are kind of like protected methods. They are never called from outside the\
    class they were from (You can call them from subclasses though)
Methods with an __ in front of them are completely private and shouldn't be overridden unless something like __str__

Also note I came from a java background and as you will see, really like OOP. Also, shutup if I forget to use the \
    format method

Also a java thing I guess, I use static typing a lot and if you see an if typing.TYPE_CHECKING somewhere, it's likely\
    because removing that (importing it normally) would cause type errors.

String convention for this project: use "" for almost everything but use '' for static typing and other smaller strings

When I reference one-way-flags, that will mean something that is set to the opposite value once. Usually, starts at \
    False then goes to True. Usually, it won't change back
"""