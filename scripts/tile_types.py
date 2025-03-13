from typing import Tuple


import numpy as np  # type: ignore
import random

import scripts.color as color


# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),   # Unicode codepoint.
        ("fg", "3B"),       # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", bool),      # True if this tile can be walked over.
        ("transparent", bool),   # True if this tile doesn't block FOV.
        ("dark", graphic_dt),       # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),      # Graphics for when this tile is in FOV.
    ]
)


def new_tile(
    *,
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles.
SHROUD = np.array((ord(" "), (255, 255, 255), color.console_bg), dtype=graphic_dt) #181425 hex bg.

# Tiles
floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("."), color.floor_dark_fg, color.console_bg),
    light=(ord("."), color.floor_light_fg, color.console_bg)
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), color.wall_dark_fg, color.console_bg),
    light=(ord("#"), (255, 255, 255), (0, 0, 0)),
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), color.stairs_down_dark, color.console_bg),
    light=(ord(">"), color.stairs_down_light, color.console_bg),
)