"""Handle the loading and initialization of game sessions."""
from __future__ import annotations


import random
import copy
import lzma
import pickle
import traceback
from typing import Optional, Tuple


import tcod
import tcod.libtcodpy

import scripts.game_data as game_data
import scripts.color as color
from scripts.engine import Engine
import scripts.entity_factories as entity_factories
import scripts.input_handlers as input_handlers
from scripts.procgen import generate_dungeon


# Load the background image and remove the alpha channel.
#background_image = tcod.image.load("resources/background_scaled.png")[:, :, :3]

def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms=game_data.max_rooms,
        room_min_size=game_data.room_min_size,
        room_max_size=game_data.room_max_size,
        map_width=game_data.map_width,
        map_height=game_data.map_height,
        max_monsters_per_room=game_data.max_monsters_per_room,
        max_items_per_room=game_data.max_items_per_room,
        engine=engine,
    )
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )
    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""  
    
    def __init__(self):
        super().__init__()
        self.frame_data = []

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the main menu on a background image."""
        #console.draw_semigraphics(background_image, 0, 0)

        self.draw_thick_frame(
            console=console,
            char_list=["@", "#", "*", "&", ".", "$", "!"],
            width=console.width,
            height=console.height - 5,
            thickness=12,
            density=200,
        )
                        
        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "CRYPTS OF THE EMBERED",
            fg=color.menu_title,
            bg=color.black,
            alignment=tcod.libtcodpy.CENTER,
            bg_blend=tcod.libtcodpy.BKGND_ALPHA(64),
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By ErinBlue",
            fg=color.menu_title,
            alignment=tcod.libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play New Game", "[C] Continue Last Game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.libtcodpy.CENTER,
                bg_blend=tcod.libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(
            self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()   # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.n:
            return input_handlers.MainGameEventHandler(new_game())
        
        return None
    
    def draw_thick_frame(self, console: tcod.console.Console, char_list: list[str], width: int, height: int, thickness: int = 2, density: int = 50) -> None:
        """
        Draws a "thick frame" made of random characters on the console and maintains its position.
        Args:
            `console (tcod.console.Console)`: The console to draw on.
            `char_list (list[str])`: List of characters to randomly use in the frame (e.g., `['@', '#', '&']`).
            `width (int)`: The width of the frame area.
            `height (int)`: The height of the frame area.
            `thickness (int)`: Thickness of the frame.
            `stored_frame (list)`: Precomputed frame data to redraw (if provided).
        
        Returns:
            list: A list of tuples (x, y, char) representing the frame data.
        """
        if not self.frame_data:
            self.frame_data = []

            # Loop to generate the frame data
            for _ in range(density):  # Arbitrary iterations for "density"
                # Randomly choose whether to draw on top, bottom, left, or right
                side = random.choice(["top", "bottom", "left", "right"])

                # Pick random characters from the char_list
                char = random.choice(char_list)

                # Pick a random color
                char_color = random.choice(color.random)

                # Determine coordinates for the frame
                if side == "top":  # Top border
                    x = random.randint(0, width - 1)
                    y = random.randint(0, thickness - 1)
                elif side == "bottom":  # Bottom border
                    x = random.randint(0, width - 1)
                    y = random.randint(height - thickness, height - 1)
                elif side == "left":  # Left border
                    x = random.randint(0, thickness - 1)
                    y = random.randint(0, height - 1)
                else:  # Right border
                    x = random.randint(width - thickness, width - 1)
                    y = random.randint(0, height - 1)

                # Store the character and its position
                self.frame_data.append((x, y, char, char_color))

        # Redraw the frame from stored data
        for x, y, char, char_color in self.frame_data:
            console.print(
                x=x,
                y=y,
                string=char,
                fg=char_color,
            )

        