from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory

from scripts.entity import Actor, Item

from scripts.color_constants import colors

# TODO: Dice rolling.
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

# Items - Consumable
health_potion = Item(
    char="!",
    color=colors["limegreen"],
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=3),
)
lightning_scroll = Item(
    char="~",
    color=colors["yellow3"],
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)
confusion_scroll = Item(
    char="~",
    color=colors["purple2"],
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
fireball_scroll = Item(
    char="~",
    color=colors["red3"],
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=18, radius=3),
)