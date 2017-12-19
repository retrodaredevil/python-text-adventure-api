"""
This package aims to add additional content to any text adventure that chooses to implement/add these features.
This means that each feature provided in these packages are optional unless they are depended on by another feature.

Some of these features will have been influenced by the battle api however, each package should not import the battle\
api. Each package, if needed, can have its own package inside the battling package that alters game play using only\
battle related events so if the person using this api chooses not to use the battle package, they still have access\
to the packages in here
"""