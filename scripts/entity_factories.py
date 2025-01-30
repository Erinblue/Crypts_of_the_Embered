from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level

from scripts.entity import Actor, Item

from scripts.color_constants import colors

# TODO: Dice rolling.
# Player
player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),   # 26 English letters
    level=Level(level_up_base=100)
)

# NPCs
imp = Actor(
    char="i",
    color=(colors["red2"]),
    name="Imp",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=300),
)
vampire = Actor(
    char="V",
    color=(colors["mediumvioletred"]),
    name="Vampire",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=1, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=300),
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

# Item - Equippable
dagger = Item(
    char="/",
    color=colors["deepskyblue1"],
    name="Dagger",
    equippable=equippable.Dagger(),
)
sword = Item(
    char="/",
    color=colors["deepskyblue1"],
    name="Sword",
    equippable=equippable.Sword(),
)
leather_armor = Item(
    char="[",
    color=colors["chocolate4"],
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)
chain_mail = Item(
    char="[",
    color=colors["chocolate4"],
    name="Chain Mail",
    equippable=equippable.ChainMail(),
)

