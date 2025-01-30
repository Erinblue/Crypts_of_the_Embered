from __future__ import annotations


from typing import Tuple, Iterable, Iterator, Optional, TYPE_CHECKING


import numpy as np  # type: ignore
import random
from tcod.console import Console


from scripts.entity import Actor, Item
import scripts.tile_types
from scripts.color_constants import RGB
import scripts.color as color


if TYPE_CHECKING:
    from scripts.engine import Engine
    from scripts.entity import Entity



class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.wall_base_color = random.choice(color.random)
        self.wall_fg_color = self.get_fg_color(self.wall_base_color)
        self.tiles = np.full((width, height), fill_value=scripts.tile_types.wall, order="F")

        
        # Tiles the player can currently see.
        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )
        # Tiles the player has seen before.
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )

        self.downstairs_location = (0, 0)

        self.initialize_map()

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))
        

    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity
            
        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None
    
    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def initialize_map(self) -> None:
        """Generate the map and precompute random wall colors using NumPy."""
        # Create an array to store the RGB color for each tile (width x height x 3 for RGB)
        self.wall_colors = np.zeros((self.width, self.height, 2, 3), dtype=int)
        
        # Loop through all tiles
        for x in range(self.width):
            for y in range(self.height):
                if not self.tiles[x, y]["walkable"] and not self.tiles[x, y]["transparent"]:  # If it's a wall

                    # Random variance.
                    hue_variation = np.random.randint(-30, 30, size=3)

                    self.wall_colors[x, y, 1] = np.clip(self.wall_base_color + hue_variation, 0, 255)  # Apply variation to gb.
                    # Apply fg color.
                    self.wall_colors[x, y, 0] = self.wall_fg_color

                    # Change fg according to bg luminance.
                    #self.tiles[x, y]["light"][1] = self.get_fg_color(self.wall_base_color)
                else:
                    # Non-wall tiles keep their original color
                    self.wall_colors[x, y, 1] = self.tiles[x, y]["light"]["bg"]


    def get_fg_color(self, bg_color: RGB) -> Tuple[int, int, int]:
        luminance = bg_color.luminance()
        return (210, 210, 210) if luminance < 128 else (20, 20, 20)
            
    def render_map(self, console: Console) -> None:
        """
        Renders the map.
        If a tile is in the "visible" array, then draw it with
        the "light" colors.
        If it isn't, but it's in the "explored" array, then draw
        it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        # Create a copy of the tiles to modify for wall colors
        tiles_with_wall_colors = self.tiles["light"].copy()

        # Mask for wall tiles (non-walkable and non-transparent)
        wall_mask = ~self.tiles["walkable"] & ~self.tiles["transparent"]

        # Replace the background color ('bg') of wall tiles with precomputed colors
        tiles_with_wall_colors["bg"][wall_mask] = self.wall_colors[wall_mask, 1]
        tiles_with_wall_colors["fg"][wall_mask] = self.wall_colors[wall_mask, 0]

        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[tiles_with_wall_colors, self.tiles["dark"] ],
            default=scripts.tile_types.SHROUD,
        )

    def render_entities(self, console: Console) -> None:
        """Renders all entities visible to the player."""
        
        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in FOV.
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color
                )


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from scripts.procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )