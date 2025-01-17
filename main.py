#!E:\Alejandro\Python\Scripts\python
import copy
import traceback

import tcod

import os

import scripts.game_data
import scripts.color as color

from scripts.engine import Engine
import scripts.entity_factories
from scripts.procgen import generate_dungeon


def main():
    screen_width = scripts.game_data.screen_width
    screen_height = scripts.game_data.screen_height

    map_width = scripts.game_data.map_width
    map_height = scripts.game_data.map_height

    room_max_size = scripts.game_data.room_max_size
    room_min_size = scripts.game_data.room_min_size
    max_rooms = scripts.game_data.max_rooms

    max_monsters_per_room = scripts.game_data.max_monsters_per_room
    max_items_per_room = scripts.game_data.max_items_per_room
    os.environ["SDL_RENDER_SCALE_QUALITY"] = "nearest"

    tileset = tcod.tileset.load_tilesheet(
        "resources/terminal16x16_gs_ro.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    #tileset = tcod.tileset.load_truetype_font(
    #    "resources/PxPlus_HP_100LX_16x12.ttf", 16, 16
    #)

    player = copy.deepcopy(scripts.entity_factories.player)

    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
        engine=engine,
    )
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to the Crypts of the Embered!", scripts.color.welcome_text
    )

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Roguelike Tutorial",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(
            screen_width, screen_height, order="F"
        )
        context.present(root_console, keep_aspect=True, integer_scaling=True)
        while True:
            root_console.clear(bg=color.console_bg)
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)

            try:
                for event in tcod.event.wait():
                    context.convert_event(event)
                    engine.event_handler.handle_events(event)
            except Exception:  # Handle exceptions in game.
                traceback.print_exc()  # Print error to stderr.
                # Then print the error to the message log.
                engine.message_log.add_message(traceback.format_exc(), color.error)





if __name__ == "__main__":
    main()