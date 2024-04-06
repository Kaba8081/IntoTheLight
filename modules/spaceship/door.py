import pygame as pg

from modules.resources import textures

class Door(pg.sprite.Sprite):
    def __init__(self, 
                 pos: tuple, 
                 sprite_group: pg.sprite.Group,
                 vertical: bool = False
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)

        self.txt_set = textures["door"]
        self.txt_closed = pg.transform.rotate(self.txt_set["closed"],90) if vertical else self.txt_set["closed"]
        self.txt_open = pg.transform.rotate(self.txt_set["open"],90) if vertical else self.txt_set["open"]
        self.image = self.txt_closed
        self.rect = self.image.get_rect()

        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

        self.opened = False

    def open(self) -> None:
        self.opened = not self.opened
        
        if self.opened:
            self.image = self.txt_open
        else:
            self.image = self.txt_closed