import pygame as pg

class Door(pg.sprite.Sprite):
    def __init__(self, 
                 pos: tuple, 
                 texture: pg.Surface, 
                 sprite_group: pg.sprite.Group,
                 vertical: bool = False
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)
        self.image = pg.transform.rotate(texture,90) if vertical else texture
        self.rect = self.image.get_rect()

        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

    def update(self) -> bool:
        pass