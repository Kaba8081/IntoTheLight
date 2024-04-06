import pygame as pg

from modules.resources import textures

class UpgradeSlot(pg.sprite.Sprite):
    def __init__(self, 
                 pos: tuple[int, int],
                 orientation: str,
                 texture: pg.Surface,
                 sprite_group: pg.sprite.Group,
                 purpose: str = None
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)

        if purpose is not None:
            self.purpose = purpose

        if orientation == "top":
            self.image = texture
        elif orientation == "right":
            self.image = pg.transform.rotate(texture, 270)
        elif orientation == "bottom":
            self.image = pg.transform.flip(texture, False, True)
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
                 orientation: str,
                 weapon_type: str,
                 sprite_group: pg.sprite.Group,
                 ) -> None:
        
        self.weapon_type = weapon_type

        self.txt_set = textures["weaponry"][weapon_type]
        self.anim_idle = self.txt_set["off"]
        self.anim_charge = [frame for frame in self.txt_set["charge"]]
        self.anim_ready = self.txt_set["ready"]

        UpgradeSlot.__init__(self, pos, orientation, self.anim_idle, sprite_group)

class Thruster(UpgradeSlot):
    def __init__(self, 
                 pos: tuple[int, int], 
                 orientation: str,
                 thruster_type: str,
                 sprite_group: pg.sprite.Group,
                 ) -> None:
        
        self.thruster_type = thruster_type
        self.txt_set = textures["thrusters"][thruster_type]
        self.anim_idle = self.txt_set["idle"]
        self.anim_active = self.txt_set["active"]

        UpgradeSlot.__init__(self, pos, orientation, self.anim_idle, sprite_group)

class Shield(UpgradeSlot):
    def __init__(self, 
                 pos: tuple[int, int], 
                 role: str,
                 ) -> None:
        UpgradeSlot.__init__(self, pos, role)