from scripts.entity import Entity
from scripts.color_constants import colors

player = Entity(char="@", color=(255, 255, 255), name="Player", blocks_movement=True)

imp = Entity(char="p", color=(colors["red2"]), name="Imp", blocks_movement=True)
vampire = Entity(char="V", color=(colors["mediumvioletred"]), name="Vampire", blocks_movement=True)