import pygame as pg

class UpgradeSlot(pg.sprite.Sprite):
    def __init__(self, 
                 pos: tuple[int, int],
                 orientation: str,
                 texture: pg.Surface,
                 sprite_group: pg.sprite.Group
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)

        if orientation == "top":
            self.image = texture
        elif orientation == "right":
            self.image = pg.transform.rotate(texture, 270)
        elif orientation == "bottom":
            self.image = pg.transform.rotate(texture, 180)
        elif orientation == "left":
            self.image = pg.transform.rotate(texture, 90)
        
        self.pos = pos
        self.rect = self.image.get_rect()

        if orientation == "top":
            self.rect.centerx = pos[0]
            self.rect.bottom = pos[1]
        elif orientation == "right":
            self.rect.left = pos[0]
            self.rect.centery = pos[1]
        elif orientation == "bottom":
            self.rect.centerx = pos[0]
            self.rect.top = pos[1]
        elif orientation == "left":
            self.rect.right = pos[0]
            self.rect.centery = pos[1]

class Weapon(UpgradeSlot):
    def __init__(self, 
                 pos: tuple[int, int], 
                 role: str,
                 ) -> None:
        UpgradeSlot.__init__(self, pos, role)

class Shield(UpgradeSlot):
    def __init__(self, 
                 pos: tuple[int, int], 
                 role: str,
                 ) -> None:
        UpgradeSlot.__init__(self, pos, role)

class Thruster(UpgradeSlot):
    def __init__(self, 
                 pos: tuple[int, int], 
                 role: str,
                 ) -> None:
        UpgradeSlot.__init__(self, pos, role)