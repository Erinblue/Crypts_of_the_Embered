from __future__ import annotations

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

from scripts.input_handlers import MainGameEventHandler
from scripts.render_functions import render_bar, render_names_at_mouse_location
from scripts.message_log import MessageLog
import scripts.game_data
import scripts.color

if TYPE_CHECKING:
    from scripts.entity import Actor
    from scripts.game_map import GameMap
    from scripts.input_handlers import EventHandler

class Engine:
    gamemap: GameMap
    
    def __init__(self, player: Actor):
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    
    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                entity.ai.perform()


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
        self.game_map.render(console)

        self.message_log.render(
            console=console,
            x=0,
            y=scripts.game_data.map_height + 3,
            width=scripts.game_data.screen_width,
            height=6
        )

        render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=scripts.game_data.screen_width
        )

        render_names_at_mouse_location(
            console=console,
            x=0,
            y=scripts.game_data.map_height,
            engine=self
        )