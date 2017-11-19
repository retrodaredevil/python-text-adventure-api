"""
The textprint package is a package designed to make printing text simple to make nice looking CL interfaces, or\
    just a nice text based program

Note that this package is only for client side so importing this into parts of a project that are meant for server\
    side could make your project less maintainable and confusing.

Note that many of the methods in this api give you the option to flush. It is recommended to leave this blank\
    if you don't want to flush and only set it to true when you are done updating the screen and would like to display\
    the contents of it. (Don't flush every call to methods because you'll see the cursor go crazy)

Also note, that this is a separate package from textadventure, so this package doesn't import textadventure anywhere
"""