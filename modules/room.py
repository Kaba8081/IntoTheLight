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
    "bridge": pg.transform.scale(pg.image.load(path.join(texture_path,"bridge.png")),(24,24)),
}

class Room(pg.sprite.Group):
    def __init__(self, 
                 pos: tuple, 
                 room_layout: list,
                 role: str = None
                 ) -> None:
        pg.sprite.Group.__init__(self)
        self.rect = pg.Rect(
            (pos[0]*32, pos[1]*32), 
            (len(room_layout)*32, len(room_layout[0])*32))

        self.pos = pos
        self.room_layout = room_layout
        self.role = role if role else None
        self.icon = textures[self.role] if self.role else None
        self.adjecent_rooms = {} # room class : connected tiles
        self.selected = False
        self.hovering = False

        for x, collumn in enumerate(self.room_layout):
            for y, tile in enumerate(collumn):
                tile = Tile(self.pos, (x, y), textures["tile_default"], self)
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

        for spr in sprites: # draw all tiles
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
            
        if self.icon: # draw icon if the room has a role
            screen.blit(self.icon, 
                        (self.rect.centerx-(self.icon.get_width()/2), 
                         self.rect.centery-(self.icon.get_height()/2))
                        )
        
        # darken the room if selected or hovering
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