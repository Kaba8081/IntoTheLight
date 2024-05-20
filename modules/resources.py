from typing import Union
import pygame as pg
from os import path
import json

_FILEPATH = path.dirname(path.realpath(__file__))
_FILEPATH = path.abspath(path.join(_FILEPATH, ".."))
_CONTENT = path.join(_FILEPATH, "content")
_FONTS = path.join(_CONTENT, "fonts")
_FILEPATH = path.join(_CONTENT, "img")

pg.font.init()

def get_font(font: str ="arial", size=16, bold=False) -> pg.font.Font:
    """Return a pygame.font.Font object with the specified font, size and boldness."""
    # if font == "arial":
    #     return pg.font.Font(path.join(_FONTS, "arial.ttf"), size)
    try: 
        res_font = pg.font.Font(path.join(_FONTS, f"{font}.ttf"), size)
    except:
        print(f"Font {font} was not found in the local dir! Using default system font...")
        res_font = pg.font.SysFont("arial", size, bold=bold)

    return res_font

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

def load_ftl_image(name: Union[str, list], **kwargs) -> Union[pg.sprite.Sprite, dict]:

    default_extension = ".png"
    src_path = kwargs["basePath"] if "basePath" in kwargs.keys() else _FILEPATH
    colorkey = (255, 0, 255) # hardcoded colorkey for FTL images (may break in the future)

    try:
        if isinstance(name, list): # iterate through every name in list
            texture_dict = dict()
            
            for sprite_name in name:
                texture_dict[sprite_name] = pg.sprite.Sprite()
                texture_dict[sprite_name].image = pg.image.load(path.join(src_path, "{prefix}{name}{suffix}{extension}".format(
                    prefix=kwargs["prefix"] if "prefix" in kwargs.keys() else "",
                    suffix=kwargs["suffix"] if "suffix" in kwargs.keys() else "",
                    extension=kwargs["extension"] if "extension" in kwargs.keys() else default_extension,
                    name=sprite_name
                ))).convert_alpha()
                texture_dict[sprite_name].image.set_colorkey(colorkey, pg.RLEACCEL)
                if "size" in kwargs.keys():
                    texture_dict[sprite_name].image = pg.transform.scale(texture_dict[sprite_name].image, kwargs["size"])
                texture_dict[sprite_name].rect = texture_dict[sprite_name].image.get_rect()

            return texture_dict
        else:
            result = pg.sprite.Sprite()
            result.image = pg.image.load(path.join(src_path, "{prefix}{name}{suffix}{extension}".format(
                prefix=kwargs["prefix"] if "prefix" in kwargs.keys() else "",
                suffix=kwargs["suffix"] if "suffix" in kwargs.keys() else "",
                extension=kwargs["extension"] if "extension" in kwargs.keys() else default_extension,
                name=name
            ))).convert_alpha()
            result.image.set_colorkey(colorkey, pg.RLEACCEL)
            if "size" in kwargs.keys():
                result.image = pg.transform.scale(result.image, kwargs["size"])
            result.rect = result.image.get_rect()

            return result
    except Exception as e:
        print(f"Error loading image {name} from {src_path}! {e}")
        return pg.Surface((1,1))

def exclude_value_from_dict(input: dict, value: Union[tuple, any]) -> dict:
    """Return a new dictionary with all values that are not equal to the specified value / values."""
    if isinstance(value, tuple) or isinstance(value, list):
        return {key: input[key] for key in input.keys() if key not in value}

    return {key: input[key] for key in input.keys() if key != value}

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
            "role": "shields",
            "level": 2,
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
                "shield": {"right":"shield_mk1"}
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
                "tiles": [[1,1],[1,1]]
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
                "level": 2
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
                "level": 1,
                "upgrade_slots": {
                    "shield": {
                        "right": "shield_mk1"
                    }
                }
            }
        ]
    }
}

texture_config = {
    "icons": {
        "basePath": path.join(_FILEPATH, "icons"),
        "extension": ".png",
        "prefix": "s_",
        "suffix": {"white": "", "blue": "_blue1", "green": "_green1", "green_hover": "_green2", "grey": "_grey1", "grey_hover": "_grey2", "orange":"_orange1", "orange_hover": "_orange2", "red": "_red1", "red_hover": "_red2", "overlay": "_overlay", "overlay2": "_overlay2"}
    },
    "ui_icons": {
        "basePath": path.join(_FILEPATH, "ui_icons"),
        "extension": ".png",
        "prefix": "icon_"
    },
    "ui_top_resource_icons": {
        "basePath": path.join(_FILEPATH, "statusUI"),
        "extension": ".png",
        "prefix": "top_",
        "suffix": {"white": "_on", "red": "_on_red"}
    },
    "ui_top_shields":{
        "basePath": path.join(_FILEPATH, "statusUI"),
        "extenson": ".png",
        "prefix": "top_",
        "suffix": {"on":"_on", "off":"_off", "purple": "_purple", "red": "_red"}
    },
    "ui_top_shields_icons": {
        "basePath": path.join(_FILEPATH, "statusUI"),
        "extension": ".png",
        "prefix": "top_",
        "suffix": {"on":"_on", "off":"_off", "hacked":"_hacked", "hacked_charged":"_hacked_charged"}
    },
    "ui_top_evade_oxygen": {
        "basePath": path.join(_FILEPATH, "statusUI"),
        "extension": ".png",
        "prefix": "top_",
        "suffix": {"on": "", "both_red": "_both_red", "up_red": "_up_red", "down_red": "_down_red"}
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

def load_textures(): # use this function after initializing the display
    # add icons to textures
    for system in systems:
        textures["system_icons"][system] = dict()
        for suffix in texture_config["icons"]["suffix"].keys():
            textures["system_icons"][system][suffix] = load_ftl_image(system, suffix=texture_config["icons"]["suffix"][suffix], **exclude_value_from_dict(texture_config["icons"], "suffix"))

        additional_sprites = {
            "overlayGrey": (125, 125, 125),
            "overlayOrange": (255, 152, 48),
            "overlayRed": (255, 0, 0),
            "overlayBlue": (93, 234, 239),
        }

        for suffix, color in additional_sprites.items():
            textures["system_icons"][system][suffix] = pg.sprite.Sprite()
            textures["system_icons"][system][suffix].image = textures["system_icons"][system]["overlay"].image.copy()
            textures["system_icons"][system][suffix].rect = textures["system_icons"][system][suffix].image.get_rect()

            bildPixel = pg.surfarray.pixels3d(textures["system_icons"][system][suffix].image)
            for i in range(3):
                bildPixel[bildPixel[:,:,i] == 255, i] = color[i]

            del bildPixel

    textures["ui_icons"] = load_ftl_image(["fuel", "missiles", "drones", "scrap"], **texture_config["ui_icons"])
    
    textures["shields"] = dict()
    textures["shields"]["enemyShield"] = load_ftl_image("enemy_shields", basePath=path.join(_FILEPATH, "ship"))

    # ui top resource icons
    textures["ui_top_resource_icons"] = dict()
    for resource in ["fuel", "missiles", "drones"]:
        textures["ui_top_resource_icons"][resource] = dict()
        for suffix in texture_config["ui_top_resource_icons"]["suffix"]:
            textures["ui_top_resource_icons"][resource][suffix] = load_ftl_image(resource, suffix=texture_config["ui_top_resource_icons"]["suffix"][suffix], **exclude_value_from_dict(texture_config["ui_top_resource_icons"], "suffix"))
    # scrap icons are named differently for some reason
    textures["ui_top_resource_icons"]["scrap"] = dict()
    textures["ui_top_resource_icons"]["scrap"]["white"] = load_ftl_image("scrap", **exclude_value_from_dict(texture_config["ui_top_resource_icons"], "suffix"))
    textures["ui_top_resource_icons"]["scrap"]["red"] = load_ftl_image("scrap_red", **exclude_value_from_dict(texture_config["ui_top_resource_icons"], "suffix"))

    # ui top shields
    textures["ui_top_shields"] = dict()
    for suffix in texture_config["ui_top_shields"]["suffix"]:
        textures["ui_top_shields"][suffix] = load_ftl_image("shields4", suffix=texture_config["ui_top_shields"]["suffix"][suffix], **exclude_value_from_dict(texture_config["ui_top_shields"], "suffix"))
    textures["ui_top_shields"]["energy_shield_box"] = load_ftl_image("energy_shield_box", basePath=texture_config["ui_top_shields"]["basePath"], size=(50,10))

    textures["ui_top_shields_icons"] = dict()
    for suffix in texture_config["ui_top_shields_icons"]["suffix"]:
        textures["ui_top_shields_icons"][suffix] = load_ftl_image("shieldsquare1", suffix=texture_config["ui_top_shields_icons"]["suffix"][suffix], **exclude_value_from_dict(texture_config["ui_top_shields_icons"], "suffix"))

    # ui hull bar
    textures["ui_hull_bar"] = dict()
    textures["ui_hull_bar"]["top_hull_white"] = load_ftl_image("top_hull", basePath=path.join(_FILEPATH, "statusUI"))
    textures["ui_hull_bar"]["top_hull_red"] = load_ftl_image("top_hull_red", basePath=path.join(_FILEPATH, "statusUI"))
    textures["ui_hull_bar"]["top_hull_bar_mask"] = dict()
    colors = {"red": (255,0,0), "yellow": (255, 152, 48), "green": (100, 255, 98)}
    textures["ui_hull_bar"]["top_hull_bar_mask"]["white"] = load_ftl_image("top_hull_bar_mask", basePath=path.join(_FILEPATH, "statusUI"))
    for color in colors.keys():
        textures["ui_hull_bar"]["top_hull_bar_mask"][color] = load_ftl_image("top_hull_bar_mask", basePath=path.join(_FILEPATH, "statusUI"))
        
        bildPixel = pg.surfarray.pixels3d(textures["ui_hull_bar"]["top_hull_bar_mask"][color].image)
        for i in range(3):
            bildPixel[bildPixel[:,:,i] == 255, i] = colors[color][i]
        del bildPixel
    
    # ui top evade and oxygen
    textures["ui_top_evade_oxygen"] = dict()
    for suffix in texture_config["ui_top_evade_oxygen"]["suffix"]:
        textures["ui_top_evade_oxygen"][suffix] = load_ftl_image("evade_oxygen", suffix=texture_config["ui_top_evade_oxygen"]["suffix"][suffix], **exclude_value_from_dict(texture_config["ui_top_evade_oxygen"], "suffix"))