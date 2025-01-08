from components.ai import HostileEnemy
from components.fighter import Fighter
from scripts.entity import Actor

from scripts.color_constants import colors


player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
)

imp = Actor(
    char="p",
    color=(colors["red2"]),
    name="Imp",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
)
vampire = Actor(
    char="V",
    color=(colors["mediumvioletred"]),
    name="Vampire",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
)