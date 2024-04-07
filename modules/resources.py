import pygame as pg
from os import path

_FILEPATH = path.dirname(path.realpath(__file__))
_FILEPATH = path.abspath(path.join(_FILEPATH, ".."))
_FILEPATH = path.join(_FILEPATH, "content")
_FILEPATH = path.join(_FILEPATH, "textures")

def load_texture(name: str, new_size: tuple[int,int]=None) -> pg.Surface:
    """Load a texture from the texture_path and resize it if needed."""
    texture = pg.image.load(path.join(_FILEPATH, name))
    if new_size is not None:
        texture = pg.transform.scale(texture, new_size)
    return texture

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
            "upgrade_slots":{
                "weapon": {"top": "laster_mk1"}
            }
        },
        {
            "pos": (7, 1),
            "tiles": [[1,1,1],[1,1,1],[1,1,1],[1,1,1]],
            "role": "medbay",
            "upgrade_slots":{
                "weapon": {"top":None},
                "shield": {"right":None}
            }
        },
        {
            "pos": (1, 2),
            "tiles": [[1,1],[1,1]],
            "role": "o2"
        },
        {
            "pos": (0, 4),
            "tiles": [[1,1,1],[1,1,1],[1,1,1]],
            "role": "engines",
            "level": 1,
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
            "role": "cameras"
        },
        {
            "pos": (11, 4),
            "tiles": [[1,1],[1,1],[1,1],[1,1]],
            "role": "bridge"
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
                "role": "o2"
            },
            {
                "pos": (1, 2),
                "tiles": [[1,1],[1,1]],
                "role": "engines",
                "level": 1,
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
                "role": "weapons"
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
                "role": "medbay"
            },
            {
                "pos": (8, 3),
                "tiles": [[1,1],[1,1]],
                "role": "shields"
            },
            {
                "pos": (10, 2),
                "tiles": [[1],[1]],
            },
            {
                "pos": (10, 3),
                "tiles": [[1],[1]],
                "role": "cameras"
            },
            {
                "pos": (12, 2),
                "tiles": [[1,1],[1,1]],
                "upgrade_slots":{
                    "weapon": {
                        "top": "laser_mk1",
                        "bottom" : None
                    }
                }
            },
            {
                "pos": (14, 2),
                "tiles": [[1,1]],
                "role": "bridge"
            }
        ]
    }
}
textures = {
    # ship parts
    "door":{
        "closed": load_texture("door_closed.png"),
        "open": load_texture("door_open.png")
    },
    "tile_default": load_texture("tile1.png"),

    # system ship icons
    "engines": load_texture("engine.png",(24,24)),
    "weapons": load_texture("weapons.png",(24,24)),
    "medbay": load_texture("medbay.png",(24,24)),
    "o2": load_texture("oxygen.png",(24,24)),
    "cameras": load_texture("camera.png",(24,24)),
    "bridge": load_texture("bridge.png",(24,24)),
    "shields": None,

    # upgrade slots
    "upgrade_slot": load_texture("upgrade_slot.png"),

    # weapons
    "weaponry":
    {
        "laser_mk1":
        {
            "off": load_texture("laser_mk1_off.png"),
            "charge":[
                load_texture("laser_mk1_charge_1.png"),
                load_texture("laser_mk1_charge_2.png"),
                load_texture("laser_mk1_charge_3.png"),
            ],
            "ready": load_texture("laser_mk1_ready.png"),
        }
    },

    # thrusters
    "thrusters":
    {
        "thruster_mk1":
        {
            "idle": load_texture("thruster_mk1_idle.png"),
            "active": load_texture("thruster_mk1_active.png")
        }
    },

    # ui elements
    "engines_icon_off": pg.image.load(path.join(_FILEPATH, "engine_icon_off.png")),
    "weapons_icon": None,
    "medbay_icon": None,
    "o2_icon": None,
    "cameras_icon": None,
    "bridge_icon": None,
    "shields_icon": None,

    "engine_icon_on": pg.image.load(path.join(_FILEPATH, "engine_icon_on.png")),
}

systems = [
    "engines",
    "weapons", 
    "medbay", 
    "o2", 
    "cameras", 
    "bridge", 
    "shields"
]