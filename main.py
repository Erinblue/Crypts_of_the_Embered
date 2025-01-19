#!E:\Alejandro\Python\Scripts\python
import traceback

import tcod

import os

import scripts.game_data
import scripts.color as color


import scripts.exceptions as exceptions
import scripts.input_handlers as input_handlers
import scripts.setup_game as setup_game


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")

def main():
    screen_width = scripts.game_data.screen_width
    screen_height = scripts.game_data.screen_height

    os.environ["SDL_RENDER_SCALE_QUALITY"] = "nearest"

    tileset = tcod.tileset.load_tilesheet(
        "resources/terminal16x16_gs_ro.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
    #tileset = tcod.tileset.load_truetype_font(
    #    "resources/PxPlus_HP_100LX_16x12.ttf", 16, 16
    #)


    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

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
        try:
            while True:
                root_console.clear(bg=color.console_bg)
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise





if __name__ == "__main__":
    main()