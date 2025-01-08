from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod

import tcod
import numpy as np

import scripts.entity_factories
from scripts.game_map import GameMap
import scripts.tile_types


if TYPE_CHECKING:
    from scripts.engine import Engine


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
        room: RectangularRoom, dungeon: GameMap, maximum_monsters: int,
) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random.random() < 0.8:
                scripts.entity_factories.imp.spawn(dungeon, x, y)
            else:
                scripts.entity_factories.vampire.spawn(dungeon, x, y)


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
    max_monsters_per_room: int,
    engine: Engine,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

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
        dungeon.tiles[new_room.inner] = scripts.tile_types.floor

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = scripts.tile_types.floor

        place_entities(new_room, dungeon, max_monsters_per_room)

        # Finally, append the new room to the list.
        rooms.append(new_room)
    
    return dungeon

