from __future__ import annotations

import random
from typing import Optional, Dict, Iterator, List, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod

import tcod
import numpy as np

from scripts.game_data import MAX_FLOOR
import scripts.entity_factories as entity_factories
from scripts.game_map import GameMap
import scripts.tile_types as tile_types


if TYPE_CHECKING:
    from scripts.engine import Engine
    from scripts.entity import Entity


# TODO: Adjust item and enemy chance and ratio to custom.
max_items_by_floor = [
    (1, 1),
    (3, 2),
]

max_monsters_by_floor = [
    (1, 1),
    (3, 2),
    (4, 3),
]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35), (entity_factories.confusion_scroll, 20), (entity_factories.sword, 15)],
    2: [(entity_factories.lightning_scroll, 25), (entity_factories.chain_mail, 15), (entity_factories.sword, 20)],
    3: [(entity_factories.fireball_scroll, 20)],
    4: [(entity_factories.lightning_scroll, 40), (entity_factories.fireball_scroll, 30), (entity_factories.health_potion, 45)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.imp, 80)],
    2: [(entity_factories.vampire, 15)],
    3: [(entity_factories.vampire, 30), (entity_factories.minotaur, 8)],
    5: [(entity_factories.vampire, 60)],
}

def get_max_value_for_floor(
        max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value

    return current_value


def get_entities_at_random(
    weighted_chance_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
    exclude: Optional[List[Entity]] = None,
) -> List[Entity]:
    entity_weighted_chances = {}

    if exclude is None:
        exclude = []

    for key, values in weighted_chance_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                if entity not in exclude:
                    weighted_chance = value[1]

                    entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )

    return chosen_entities


# Base Room.
class Room:
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y
    
    @abstractmethod
    def inner(self) -> Tuple[slice, slice] | Tuple[np.ndarray, np.ndarray]:
        """
        Return the inncer area of the room.
        Subclasses must overwrite this function accordingly.
        """
        pass

    def intersects(self, other: Room) -> bool:
        """Return True if this room overlaps with another Room."""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


# Basic Rectangular Room
class RectangularRoom(Room):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x1=x, y1=y, x2=x + width, y2=y + height)
    
    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)


# TODO: Base Circular Room
class CircularRoom(Room):
    def __init__(self, x, y, radius):
        super().__init__(x1=x, y1=y, x2=x+radius, y2=y+radius)
        self.radius = radius
        self.cx, self.cy = super().center

    @property
    def inner(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the inner area of this room as the exact circular area.
        """
        y, x = np.mgrid[self.y1:self.y2+1, self.x1:self.x2+1]

        # Circle equation
        circle_mask = ((x - self.cx) ** 2 + (y - self.cy) ** 2) <= self.radius ** 2

        return np.where(circle_mask)


# TODO: Basic Eliptical Room
class ElipticalRoom(Room):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x1=x, y1=y, x2=x + width, y2=y + height)
        self.cx = self.center[0]
        self.cy = self.center[1]
        self.radius_x = width / 2
        self.radius_y = height / 2

    @property
    def inner(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the inner area of this room as the exact ellipse-shaped area.
        This returns a tuple of two numpy arrays: (x_indices, y_indices).
        """
        y, x = np.mgrid[self.y1:self.y2+1, self.x1:self.x2+1]
        ellipse_mask = (((x - self.cx) ** 2) / (self.radius_x ** 2) +
                        ((y - self.cy) ** 2) / (self.radius_y ** 2)) <= 1
        return np.where(ellipse_mask)


def place_entities(
        room: RectangularRoom, dungeon: GameMap, floor_number: int
) -> None:
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
    )

    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number, exclude=[entity_factories.amulet_of_yendor]
    )

    # Check if the Amulet of Yendor should be placed
    if not dungeon.amulet_placed and floor_number == MAX_FLOOR:  # MAX_FLOOR is the last floor
        items.append(entity_factories.amulet_of_yendor)
        dungeon.amulet_placed = True  # Mark the Amulet as placed

    for entity in monsters + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity.spawn(dungeon, x, y)

def tunnel_between(
        start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int,int]]:
    """Return an L-shaped tunnel between these two points."""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:   # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    # Generate the coordinates for this tunnel.
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    center_of_last_room = (0, 0)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor
            center_of_last_room = new_room.center

        place_entities(new_room, dungeon, engine.game_world.current_floor)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

        # Finally, append the new room to the list.
        rooms.append(new_room)
    
    return dungeon

