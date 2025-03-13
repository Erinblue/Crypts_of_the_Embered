from __future__ import annotations

import lzma
import pickle
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov
from libtcodpy import (
    FOV_BASIC,
    FOV_DIAMOND,
    FOV_PERMISSIVE,
    FOV_RESTRICTIVE,
    FOV_SHADOW,
    FOV_SYMMETRIC_SHADOWCAST,
)

import scripts.exceptions as exceptions
import scripts.render_functions as render_functions
from scripts.translation import Translation
from scripts.message_log import MessageLog
import scripts.game_data as game_data
import scripts.color

if TYPE_CHECKING:
    from scripts.entity import Actor
    from scripts.game_map import GameMap, GameWorld

class Engine:
    game_map: GameMap
    game_world: GameWorld
    
    def __init__(self, player: Actor):
        self.translation = Translation(language="es")
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.amulet_picked: bool = False
        self.player = player

    
    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass    # Ignore impossible action exceptions from AI.


    def update_fov(self) -> None:
        """Recompute the visible area based on the players POV."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
            algorithm=FOV_DIAMOND   # Default algorithm is FOV_RESTRICTIVE.
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible


    def render(self, console: Console) -> None:
        self.game_map.render_map(console)

        self.game_map.render_entities(console)

        self.message_log.render(
            console=console,
            x=game_data.screen_width - game_data.gui_width,
            y=game_data.map_height + 3,
            width=game_data.gui_width,
            height=6,
        )

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=game_data.screen_width,
            engine=self,
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(1, game_data.map_height + 3),
            engine=self,
        )
        render_functions.render_names_at_mouse_location(
            console=console,
            x=1,
            y=game_data.map_height,
            engine=self,
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)