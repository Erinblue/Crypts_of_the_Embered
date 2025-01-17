from components.ai import HostileEnemy
from components.consumable import HealingConsumable
from components.fighter import Fighter
from components.inventory import Inventory

from scripts.entity import Actor, Item

from scripts.color_constants import colors

# Player
player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
    inventory=Inventory(capacity=26),
)

# NPCs
imp = Actor(
    char="i",
    color=(colors["red2"]),
    name="Imp",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
    inventory=Inventory(capacity=0),
)
vampire = Actor(
    char="V",
    color=(colors["mediumvioletred"]),
    name="Vampire",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
    inventory=Inventory(capacity=0),
)

# Items
health_potion = Item(
    char="!",
    color=colors["limegreen"],
    name="Health Potion",
    consumable=HealingConsumable(amount=3)
)