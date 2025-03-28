from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Tuple

from collections import Counter

import scripts.color
import scripts.game_data

if TYPE_CHECKING:
    from tcod import Console
    from scripts.engine import Engine
    from scripts.game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""       
    names: Iterable = []

    for entity in game_map.entities:
        if entity.x == x and entity.y == y:
            names.append(entity.name)

    names_counter = Counter(names)

    names_list = []
    
    for name in names_counter.keys():
        count = names_counter[name]
        if count > 1:
            names_list.append(f"{name}(x{count})")
        elif count == 1:
            names_list.append(f"{name}")

    formatted_names = ", ".join(names_list)
    
    return formatted_names.capitalize()


def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int, engine: Engine
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    if bar_width > 0:
        console.draw_rect(
            x=0, y=scripts.game_data.map_height + 1, width=bar_width, height=1, ch=1, bg=scripts.color.bar_filled
        )

    console.print(
        x=1, y=scripts.game_data.map_height + 1, string=f"{engine.translation.translate("hp")}: {current_value}/{maximum_value}", fg=scripts.color.bar_text
    )


def render_dungeon_level(
        console: Console, dungeon_level: int, location: Tuple[int,int], engine: Engine
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location
    console.print(x=x, y=y, string=engine.translation.translate("floor", dungeon_level=dungeon_level))


def render_names_at_mouse_location(
        console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    console.print(x=x, y=y, string=names_at_mouse_location)