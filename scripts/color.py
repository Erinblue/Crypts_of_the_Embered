from scripts.color_constants import RGB, colors


white = colors["white"]
black = colors["black"]
red = colors["red1"]
red1 = colors["red1"]
red2 = colors["red2"]
red3 = colors["red3"]
red4 = colors["red4"]
firebrick4 = colors["firebrick4"]

lightgrey = colors["lightgrey"]
coldgrey = colors["coldgrey"]
warmgrey = colors["warmgrey"]

player_atk = colors["lightyellow3"]
enemy_atk = colors["orange1"]
needs_target = (0x3F, 0xFF, 0xFF)
status_effect_applied = (0x3F, 0xFF, 0x3F)
descend = (0x9F, 0x3F, 0xFF)

player_die = colors["orangered1"]
enemy_die = colors["indianred3"]

invalid = (0xFF, 0xFF, 0x00)
impossible = (0x80, 0x80, 0x80)
error = (0xFF, 0x40, 0x40)

welcome_text = colors["cadetblue1"]
health_recovered = (0x0, 0xFF, 0x0)

bar_text = white
bar_filled = colors["cobaltgreen"]
bar_empty = colors["brown2"]

menu_title = colors["lightskyblue2"]
menu_text = white

constitution = bar_filled
strength = colors["orangered2"]
agility = colors["cadmiumyellow"]

random = [
    colors["teal"],
    colors["lightskyblue2"],
    colors["purple2"],
    colors["firebrick4"],
    colors["orange3"],
    colors["lightyellow3"],
    colors["limegreen"],
    colors["cobaltgreen"],
    colors["lightgrey"],
]
# Tiles
console_bg = (3, 9, 20)
wall_dark_bg = (30, 30, 30)
floor_light_fg = (210, 210, 210)
floor_dark_fg = (100, 100, 100)
wall_light_fg = (255, 255, 255)
wall_dark_fg = (100, 100, 100)

stairs_down_light = colors["teal"]
stairs_down_dark = colors["midnightblue"]












