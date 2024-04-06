import pygame as pg
from os import path

from modules.spaceship.tile import Tile
from modules.spaceship.upgrades import *

file_path = path.dirname(path.realpath(__file__))
texture_path = path.abspath(path.join(path.join(file_path, ".."),".."))
texture_path = path.join(texture_path, "content")
texture_path = path.join(texture_path, "textures")

textures = {
    "tile_default": pg.image.load(path.join(texture_path,"tile1.png")),
    "engines": pg.transform.scale(pg.image.load(path.join(texture_path,"engine.png")),(24,24)),
    "weapons": pg.transform.scale(pg.image.load(path.join(texture_path,"weapons.png")),(24,24)),
    "medbay": pg.transform.scale(pg.image.load(path.join(texture_path,"medbay.png")),(24,24)),
    "o2": pg.transform.scale(pg.image.load(path.join(texture_path,"oxygen.png")),(24,24)),
    "cameras": pg.transform.scale(pg.image.load(path.join(texture_path,"camera.png")),(24,24)),
    "bridge": pg.transform.scale(pg.image.load(path.join(texture_path,"bridge.png")),(24,24)),
    "shields": None,
    "upgrade_slot": pg.image.load(path.join(texture_path,"upgrade_slot.png")),
}

class Room(pg.sprite.Group):
    def __init__(self, 
                 pos: tuple[int, int], 
                 room_layout: list,
                 role: str = None,
                 upgrade_slots: dict[str, str] = {},
                 enemy_ship: bool = False
                 ) -> None:
        pg.sprite.Group.__init__(self)
        self.rect = pg.Rect(
            (pos[0]*32, pos[1]*32), 
            (len(room_layout)*32, len(room_layout[0])*32))

        self.pos = pos
        self.room_layout = room_layout
        self.role = role if role is not None else None
        self.icon = None
        if self.role is not None:
            self.icon = textures[self.role]
            self.icon = pg.transform.flip(self.icon, True, False) if enemy_ship else self.icon
        self.adjecent_rooms = {} # room class : connected tiles
        self.upgrade_slots = {}

        self.selected = False
        self.hovering = False

        for x, collumn in enumerate(self.room_layout):
            for y, tile in enumerate(collumn):
                tile = Tile(self.pos, (x, y), textures["tile_default"], self)
                self.add(tile)

        for index, upgrade in enumerate(upgrade_slots):
            if type(upgrade_slots[upgrade]) is str:
                self.place_upgrade(index, upgrade, upgrade_slots[upgrade])
            else:
                for orientation in upgrade_slots[upgrade]:
                    self.place_upgrade(index, upgrade, orientation)

    def update(self, mouse_pos: tuple[int, int], mouse_clicked: bool) -> None:
        if self.rect.collidepoint(mouse_pos):
            if mouse_clicked[0]:
                self.selected = True
                self.hovering = False
            else:
                self.hovering = True

            return
            
        self.hovering = False
        if mouse_clicked[0] and self.selected:
            self.selected = False

    def draw(self, screen) -> None:
        sprites = self.sprites()

        # draw all sprites in the room
        for spr in sprites:
            self.spritedict[spr] = screen.blit(spr.image, spr.rect)
        
        # draw room outline
        pg.draw.lines(
            screen, 
            (89,86,82), 
            True, 
            [
                # top left -> top right 
                (self.rect.x, self.rect.y),
                (self.rect.x+self.rect.width, self.rect.y), 
                # top right -> bottom right
                (self.rect.x+self.rect.width, self.rect.y), 
                (self.rect.x+self.rect.width, self.rect.y+self.rect.height),
                # bottom right -> bottom left
                (self.rect.x+self.rect.width, self.rect.y+self.rect.height),
                (self.rect.x, self.rect.y+self.rect.height),
                # bottom left -> top left
                (self.rect.x, self.rect.y+self.rect.height),
                (self.rect.x, self.rect.y)
            ],
            4
        )

        # draw icon if the room has a role
        if self.icon is not None:
            screen.blit(self.icon, 
                        (self.rect.centerx-(self.icon.get_width()/2), 
                         self.rect.centery-(self.icon.get_height()/2))
                        )
        
        # darken the room if selected or hovering
        if self.selected: 
            s = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA) 
            s.fill((0,0,0,128))
            screen.blit(s, self.rect)
        elif self.hovering:
            s = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA) 
            s.fill((0,0,0,64)) 
            screen.blit(s, self.rect)
    
    def place_upgrade(self, index: int, upgrade_type: str, orientation: str) -> None:
        # TODO: check upgrade_type and create correspoding class
        upgrade_pos = None

        match orientation:
            case "top":
                upgrade_pos = (self.rect.centerx, self.rect.y)
            case "right":
                upgrade_pos = (self.rect.right, self.rect.centery)
            case "bottom":
                upgrade_pos = (self.rect.centerx, self.rect.bottom)
            case "left":
                upgrade_pos = (self.rect.x, self.rect.centery)
        
        self.upgrade_slots[index] = UpgradeSlot(upgrade_pos, orientation, textures["upgrade_slot"], self)