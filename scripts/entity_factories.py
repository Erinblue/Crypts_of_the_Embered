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
    name="Jugador",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),   # 26 English letters
    level=Level(level_up_base=5, level_up_factor=5)
)

# NPCs
imp = Actor(
    char="d",
    color=(colors["red3"]),
    name="Diablillo",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=2),
)
minotaur = Actor(
    char="m",
    color=(colors["red3"]),
    name="Minotauro",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=18, base_defense=1, base_power=5),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=16),
)
vampire = Actor(
    char="V",
    color=(colors["mediumvioletred"]),
    name="Vampiro",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=1, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=8),
)

# Items - Consumable
health_potion = Item(
    char="!",
    color=colors["limegreen"],
    name="Poción de Salud",
    consumable=consumable.HealingConsumable(amount=3),
)
lightning_scroll = Item(
    char="~",
    color=colors["yellow3"],
    name="Pergamino Relámpago",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)
confusion_scroll = Item(
    char="~",
    color=colors["mediumpurple1"],
    name="Pergamino Confusión",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
fireball_scroll = Item(
    char="~",
    color=colors["red3"],
    name="Pergamino Explosión",
    consumable=consumable.FireballDamageConsumable(damage=18, radius=3),
)

# Item - Equippable
dagger = Item(
    char="/",
    color=colors["deepskyblue1"],
    name="Daga",
    equippable=equippable.Dagger(),
)
sword = Item(
    char="/",
    color=colors["deepskyblue1"],
    name="Espada",
    equippable=equippable.Sword(),
)
leather_armor = Item(
    char="[",
    color=colors["chocolate4"],
    name="Armadura Cuero",
    equippable=equippable.LeatherArmor(),
)
chain_mail = Item(
    char="[",
    color=colors["chocolate4"],
    name="Cota de Malla",
    equippable=equippable.ChainMail(),
)

# Amulet Of Yendor
amulet_of_yendor = Item(
    char="♀",
    color=colors["darkgoldenrod2"],
    name="Amuleto de Yendor",
    yendor=True,
)

