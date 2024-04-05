import pygame as pg
from os import path

from modules.tile import Tile

file_path = path.dirname(path.realpath(__file__))
texture_path = path.abspath(path.join(file_path, ".."))
texture_path = path.join(texture_path, "content")
texture_path = path.join(texture_path, "textures")

textures = {
    "tile_default": pg.image.load(path.join(texture_path,"tile1.png")),
    "engines": pg.transform.scale(pg.image.load(path.join(texture_path,"engine.png")),(24,24)),
    "weapons": pg.transform.scale(pg.image.load(path.join(texture_path,"weapons.png")),(24,24)),
    "medbay": pg.transform.scale(pg.image.load(path.join(texture_path,"medbay.png")),(24,24)),
    "o2": pg.transform.scale(pg.image.load(path.join(texture_path,"oxygen.png")),(24,24)),
    "cameras": pg.transform.scale(pg.image.load(path.join(texture_path,"camera.png")),(24,24)),
    "bridge": pg.transform.scale(pg.image.load(path.join(texture_path,"bridge.png")),(24,24))
}

class Room(pg.sprite.Group):
    def __init__(self, 
                 pos: tuple, 
                 room_layout: list,
                 role: str = None
                 ) -> None:
        pg.sprite.Group.__init__(self)
        self.rect = pg.Rect(pos, (len(room_layout)*32, len(room_layout[0])*32))

        self.pos = pos
        self.room_layout = room_layout
        self.role = role if role else None
        self.icon = textures[self.role] if self.role else None

        self.selected = False
        self.hovering = False

        for x, collumn in enumerate(self.room_layout):
            for y, tile in enumerate(collumn):
                tile = Tile(self.pos, (x*32, y*32), textures["tile_default"], self)
                self.add(tile)

    def update(self, mouse_pos: tuple, mouse_clicked: bool) -> None:
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

        for spr in sprites:
            self.spritedict[spr] = screen.blit(spr.image, spr.rect)
        if self.icon:
            screen.blit(self.icon, (self.rect.centerx-12, self.rect.centery-12))

        if self.selected:
            s = pg.Surface((32,32), pg.SRCALPHA) 
            s.fill((0,0,0,128)) 
            for spr in sprites:
                screen.blit(s, spr.rect)

        elif self.hovering:
            s = pg.Surface((32,32), pg.SRCALPHA) 
            s.fill((0,0,0,64)) 
            for spr in sprites:
                screen.blit(s, spr.rect)