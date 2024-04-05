import pygame as pg

from modules.room import Room

ship_layouts = {
    "cruiser": 
    {
        "rooms":
        [ 
        {
            "pos": (64, 64),
            "tiles": [[1,1],[1,1],[1,1]]
        },
        {
            "pos": (160, 96),
            "tiles": [[1,1,1],[1,1,1],[1,1,1],[1,1,1]],
            "role": "weapons"
        },
        {
            "pos": (288, 96),
            "tiles": [[1,1,1],[1,1,1],[1,1,1],[1,1,1]],
            "role": "medbay"
        },
        {
            "pos": (96, 128),
            "tiles": [[1,1],[1,1]],
            "role": "o2"
        },
        {
            "pos": (64, 192),
            "tiles": [[1,1,1],[1,1,1],[1,1,1]],
            "role": "engines"
        },
        {
            "pos": (160, 256),
            "tiles": [[1,1],[1,1],[1,1],[1,1],[1,1],[1,1]]
        },
        {
            "pos": (288, 192),
            "tiles": [[1,1],[1,1],[1,1],[1,1]],
            "role": "cameras"
        },
        {
            "pos": (416, 192),
            "tiles": [[1,1],[1,1],[1,1],[1,1]],
            "role": "bridge"
        }
        ]
    }
}

class Player():
    def __init__(self, 
                 ship_type: str = "cruiser"
                 ) -> None:
        
        self.rooms = []
        for room in ship_layouts[ship_type]["rooms"]:
            self.rooms.append(Room(
                room["pos"], 
                room["tiles"],
                room["role"] if "role" in room else None)
                )
    
    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pg.Surface) -> None:
        for group in self.rooms:
            group.draw(screen)