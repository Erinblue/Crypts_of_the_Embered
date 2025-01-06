from __future__ import annotations


from typing import Iterable, Optional, TYPE_CHECKING


import numpy as np  # type: ignore
from tcod.console import Console


import scripts.tile_types

if TYPE_CHECKING:
    from scripts.entity import Entity


class GameMap:
    def __init__(self, width: int, height: int, entities: Iterable[Entity] = ()):
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=scripts.tile_types.wall, order="F")

        # Tiles the player can currently see.
        self.visible = np.full((width, height), fill_value=False, order="F")
        # Tiles the player has seen before.
        self.explored = np.full((width, height), fill_value=False, order="F")
        self.initialize_map()

    def get_blocking_entity_at_location(self, location_x: int, location_y: int) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity
            
        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def initialize_map(self) -> None:
        """Generate the map and precompute random wall colors using NumPy."""
        # Create an array to store the RGB color for each tile (width x height x 3 for RGB)
        self.wall_colors = np.zeros((self.width, self.height, 3), dtype=int)
        
        # Generate a random hue variation for wall tiles

        # Loop through all tiles
        for x in range(self.width):
            for y in range(self.height):
                if not self.tiles[x, y]["walkable"] and not self.tiles[x, y]["transparent"]:  # If it's a wall
                    # Get the base light bg color
                    base_color = np.array(self.tiles[x, y]["light"][2])
                    # Random variance.
                    hue_variation = np.random.randint(-30, 30, size=3)

                    self.wall_colors[x, y] = np.clip(base_color + hue_variation, 0, 255)  # Apply variation
                else:
                    # Non-wall tiles keep their original color
                    self.wall_colors[x, y] = self.tiles[x, y]["light"][2]

            
    def render(self, console: Console) -> None:
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
        tiles_with_wall_colors["bg"][wall_mask] = self.wall_colors[wall_mask]

        console.rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[tiles_with_wall_colors, self.tiles["dark"] ],
            default=scripts.tile_types.SHROUD
        )

        for entity in self.entities:
            # Only print entities that are in FOV.
            if self.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)