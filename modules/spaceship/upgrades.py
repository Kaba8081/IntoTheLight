import pygame as pg

from modules.resources import textures, weapon_names

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
            # purpose is a string that describes only the upgrade slot
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
                 weapon_name: str,
                 sprite_group: pg.sprite.Group,
                 ) -> None:

        self._txt_set = textures["weaponry"][weapon_name]
        self._anim_idle = self._txt_set["off"]
        self._anim_charge = [frame for frame in self._txt_set["charge"]]
        self._anim_ready = self._txt_set["ready"]

        self.weapon_name = weapon_name
        self.display_name = weapon_names[weapon_name]
        self.state = "off" # off | charge | ready
        UpgradeSlot.__init__(self, pos, orientation, self._anim_idle, sprite_group)

    def __str__(self) -> str:
        """Return the name of the weapon."""
        return self.display_name

    def __bool__(self) -> bool:
        """Return True if the weapon is ready to fire."""
        return self.state == "ready"

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