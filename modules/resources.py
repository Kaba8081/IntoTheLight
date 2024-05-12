import pygame as pg
from os import path
import json

_FILEPATH = path.dirname(path.realpath(__file__))
_FILEPATH = path.abspath(path.join(_FILEPATH, ".."))
_CONTENT = path.join(_FILEPATH, "content")
_FILEPATH = path.join(_CONTENT, "img")

pg.font.init()

def get_font(font: str ="arial", size=16, bold=False) -> pg.font.Font:
    """Return a pygame.font.Font object with the specified font, size and boldness."""

    try: 
        return pg.font.Font(path.join(_CONTENT, f"{font}.ttf"), size)
    except:
        print(f"Font {font} was not found in the local dir! Using default system font...")
        return pg.font.SysFont("arial", size, bold=bold)

def load_config() -> dict:
    with open("config.json", "r", encoding="utf-8-sig") as file:
        return json.load(file)

def load_texture(name: str, new_size: tuple[int,int]=None, extension: str=".png") -> pg.Surface:
    """Load a texture from the texture_path and resize it if needed."""

    name += extension
    texture =  pg.image.load(path.join(_FILEPATH, name))
    if new_size is not None:
        texture = pg.transform.scale(texture, new_size)
    return texture

def autocomplete_configs(config: dict, config_str: str) -> dict:
    """Autocomplete the config with the missing values."""

    match config_str:
        case "button_palletes":
            for pallete_id in button_palletes.keys():
                for category in button_palletes[pallete_id].keys():
                    states = button_palletes[pallete_id][category].keys()
                    
                    if "normal" not in states:
                        button_palletes[pallete_id][category]["normal"] = (0,0,0)
                    if "normal_hover" not in states:
                        button_palletes[pallete_id][category]["normal_hover"] = button_palletes[pallete_id][category]["normal"]
                    if "clicked" not in states:
                        button_palletes[pallete_id][category]["clicked"] = (0,0,0)
                    if "clicked_hover" not in states:
                        button_palletes[pallete_id][category]["clicked_hover"] = button_palletes[pallete_id][category]["clicked"]

CONFIG = load_config()

keybinds = {
    "select_weapon1" : pg.K_1,
    "select_weapon2" : pg.K_2,
    "select_weapon3" : pg.K_3,
    "select_weapon4" : pg.K_4,
}

ship_layouts = {
    "cruiser": 
    {
        "rooms":
        [ 
        {
            "pos": (0, 0),
            "tiles": [[1,1],[1,1],[1,1]],
            "upgrade_slots":{
                "thruster": {"left": None}
            }
        },
        {
            "pos": (3, 1),
            "tiles": [[1,1,1],[1,1,1],[1,1,1],[1,1,1]],
            "role": "weapons",
            "level": 3,
            "upgrade_slots":{
                "weapon": {"top": "laster_mk1"}
            }
        },
        {
            "pos": (7, 1),
            "tiles": [[1,1,1],[1,1,1],[1,1,1],[1,1,1]],
            "role": "medbay",
            "level": 1,
            "upgrade_slots":{
                "weapon": {"top":None},
                "shield": {"right":None}
            }
        },
        {
            "pos": (1, 2),
            "tiles": [[1,1],[1,1]],
            "role": "oxygen",
            "level": 1
        },
        {
            "pos": (0, 4),
            "tiles": [[1,1,1],[1,1,1],[1,1,1]],
            "role": "engines",
            "level": 2,
            "upgrade_slots":{
                "thruster": {"left": "thruster_mk1"}
            }
        },
        {
            "pos": (3, 6),
            "tiles": [[1,1],[1,1],[1,1],[1,1],[1,1],[1,1]],
            "upgrade_slots":{
                "weapon": {"bottom": "laser_mk1"}
            }
        },
        {
            "pos": (7, 4),
            "tiles": [[1,1],[1,1],[1,1],[1,1]],
            "role": "sensors",
            "level": 1,
        },
        {
            "pos": (11, 4),
            "tiles": [[1,1],[1,1],[1,1],[1,1]],
            "role": "pilot",
            "level": 1
        }
        ]
    },
    "scout":{
        "rooms":[
            {
                "pos": (0, 2),
                "tiles": [[1,1]],
                "upgrade_slots":{
                    "thruster": {"left" : "thruster_mk1"}
                }
            },
            {
                "pos": (1, 1),
                "tiles": [[1],[1]],
                "role": "oxygen",
                "level": 1
            },
            {
                "pos": (1, 2),
                "tiles": [[1,1],[1,1]],
                "role": "engines",
                "level": 3,
            },
            {
                "pos": (1, 4),
                "tiles": [[1],[1]],
            },
            {
                "pos": (3, 1),
                "tiles": [[1],[1]]
            },
            {
                "pos": (3, 4),
                "tiles": [[1],[1]],
            },
            {
                "pos": (4, 2),
                "tiles": [[1,1],[1,1]],
                "role": "weapons",
                "level": 2
            },
            {
                "pos": (6, 0),
                "tiles": [[1],[1]],
            },
            {
                "pos": (6, 1),
                "tiles": [[1,1],[1,1]],
            },
            {
                "pos": (6, 3),
                "tiles": [[1,1],[1,1]],
            },
            {
                "pos": (6, 5),
                "tiles": [[1],[1]],
            },
            {
                "pos": (8, 1),
                "tiles": [[1,1],[1,1]],
                "role": "medbay",
                "level": 1,
                "upgrade_slots":{
                    "weapon": {
                        "top": "laser_mk2",
                    }
                }
            },
            {
                "pos": (8, 3),
                "tiles": [[1,1],[1,1]],
                "role": "shields",
                "level": 1
            },
            {
                "pos": (10, 2),
                "tiles": [[1],[1]],
            },
            {
                "pos": (10, 3),
                "tiles": [[1],[1]],
                "role": "sensors",
                "level": 1,
                "upgrade_slots":{
                    "weapon": {
                        "bottom" : "laser_mk1"
                    }
                }
            },
            {
                "pos": (12, 2),
                "tiles": [[1,1],[1,1]],
                "upgrade_slots":{
                    "weapon": {
                        "top": "laser_mk1",
                        "bottom" : "laser_mk1"
                    }
                }
            },
            {
                "pos": (14, 2),
                "tiles": [[1,1]],
                "role": "pilot",
                "level": 1
            }
        ]
    }
}

texture_config = {
    "icons": {
        "basePath": path.join(_FILEPATH, "icons"),
        "extension": ".png",
        "prefix": "s_",
        "suffix": "_overlay",
    },
    "ui_icons": {
        "basePath": path.join(_FILEPATH, "ui_icons"),
        "extension": ".png",
        "prefix": "icon_"
    }
}

textures = {
    # ship parts
    "door":{
        "closed": load_texture("door_closed"),
        "open": load_texture("door_open")
    },
    "tile_default": load_texture("tile1"),

    "system_icons": {},
    "ui_icons": {},

    # upgrade slots
    "upgrade_slot": load_texture("upgrade_slot"),

    # weapons
    "weaponry":
    {
        "laser_mk1":
        {
            "disabled": load_texture("laser_mk1_off"),
            "charging":[
                load_texture("laser_mk1_charge_1"),
                load_texture("laser_mk1_charge_2"),
                load_texture("laser_mk1_charge_3"),
            ],
            "ready": load_texture("laser_mk1_ready"),
        },
        "laser_mk2":
        {
            "disabled": load_texture("laser_mk1_off"),
            "charging":[
                load_texture("laser_mk1_charge_1"),
                load_texture("laser_mk1_charge_2"),
                load_texture("laser_mk1_charge_3"),
            ],
            "ready": load_texture("laser_mk1_ready"),
        }
    },

    # thrusters
    "thrusters":
    {
        "thruster_mk1":
        {
            "idle": load_texture("thruster_mk1_idle"),
            "active": load_texture("thruster_mk1_active")
        }
    },

    # shield upgrades
    "shield_upgrades": {
        "shield_mk1": load_texture("laser_mk1_off")
    },

    # ui elements
    "shields_icon_off":  load_texture("engine_icon_off"),
    "engines_icon_off":  load_texture("engine_icon_off"),
    "oxygen_icon_off":  load_texture("engine_icon_off"),
    "medbay_icon_off":  load_texture("engine_icon_off"),
    "weapons_icon_off":  load_texture("weapons_icon_off"),
    "drones_icon_off":  load_texture("engine_icon_off"),
    "pilot_icon_off":  load_texture("engine_icon_off"),
    "sensors_icon_off":  load_texture("engine_icon_off"),
    "doors_icon_off": load_texture("engine_icon_off"),

    "shields_icon_on":  load_texture("engine_icon_on"),
    "engines_icon_on":  load_texture("engine_icon_on"),
    "oxygen_icon_on":  load_texture("engine_icon_on"),
    "medbay_icon_on":  load_texture("engine_icon_on"),
    "weapons_icon_on":  load_texture("weapons_icon_on"),
    "drones_icon_on":  load_texture("engine_icon_on"),
    "pilot_icon_on":  load_texture("engine_icon_on"),
    "sensors_icon_on":  load_texture("engine_icon_on"),
    "doors_icon_on": load_texture("engine_icon_on"),
}

# list of systems, while also defining the order in which they are sorted and drawn
systems = [
    "shields",
    "engines",
    "oxygen", 
    "medbay", 
    "weapons",
    "drones", 
    "pilot",
    "sensors", 
    "doors"
]

weapons = {
    "laser_mk1": {
        "name": "Laser MK1",
        "req_power": 1,
        "charge_time": 100,
        "volley_shots": 1,
        "volley_delay": 0.3,
        "projectile_type": "laser"
    }, 
    "laser_mk2": {
        "name": "Laser MK2",
        "req_power": 1,
        "charge_time": 100,
        "volley_shots": 3,
        "volley_delay": 0.3,
        "projectile_type": "laser"
    }
}

button_palletes = {
    "default": {
        "background":{
            "normal": (200,200,200),
            "normal_hover": (150,150,150),
            "clicked": (150, 150, 150),
            "clicked_hover": (120, 120, 120)
        },
        "border":{
            "normal": (255,255,255),
            "normal_hover": (200,200,200),
            "clicked": (150,150,150)
        },
        "label":{
            "normal": (0,0,0)
        }
    },
    "autoaim":{
        "background":{
            "normal": (200,200,200),
            "normal_hover": (150,150,150),
            "clicked": (252, 209, 91),
            "clicked_hover": (199, 158, 44)
        },
        "border":{
            "normal": (255,255,255),
            "normal_hover": (50,50,50),
            "clicked": (150,150,150),
            "clicked_hover": (120,120,120),
        },
        "label":{
            "normal": (0,0,0)
        }
        
    }
}

autocomplete_configs(button_palletes, "button_palletes")

# add icons to textures
for system in systems:
    try:
        textures["system_icons"][system] = pg.image.load(path.join(texture_config["icons"]["basePath"], "{prefix}{system}{suffix}{extension}".format(
            prefix=texture_config["icons"]["prefix"],
            suffix=texture_config["icons"]["suffix"],
            extension=texture_config["icons"]["extension"],
            system=system
        )))
    except:
        print(f"Icon for system {system} not found!")
        textures["system_icons"][system] = pg.Surface((1,1))

for currency in ["fuel", "missile", "drone_parts", "scrap"]:
    try:
        textures["ui_icons"][currency] = pg.image.load(path.join(texture_config["ui_icons"]["basePath"], "{prefix}{currency}{extension}".format(
            prefix=texture_config["ui_icons"]["prefix"],
            extension=texture_config["ui_icons"]["extension"],
            currency=currency
        )))
    except:
        print(f"Icon for currency {currency} not found!")
        textures["ui_icons"][currency] = pg.image.load(path.join(texture_config["ui_icons"]["basePath"],"icon_placeholder.png"))