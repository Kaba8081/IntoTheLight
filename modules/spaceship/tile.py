import pygame as pg

class Tile(pg.sprite.Sprite):
    def __init__(self, 
                 parent_pos: tuple, 
                 pos: tuple, 
                 texture: pg.Surface, 
                 sprite_group: pg.sprite.Group
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)
        
        self.image = texture
        self.rect = self.image.get_rect()

        self.pos = pos
        self.rect.x = parent_pos[0] + pos[0] * 32
        self.rect.y = parent_pos[1] + pos[1] * 32