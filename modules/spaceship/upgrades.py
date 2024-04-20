import pygame as pg

from modules.resources import textures, weapons

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

        self.orientation = orientation
        self.change_texture(texture)
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

    def change_texture(self, texture: pg.Surface) -> None:
        """
        Rotate the texture based on the orientation of the upgrade slot.
        :param texture: The texture to be rotated.
        """

        if self.orientation == "top":
            self.image = texture
        elif self.orientation == "right":
            self.image = pg.transform.rotate(texture, 270)
        elif self.orientation == "bottom":
            self.image = pg.transform.flip(texture, False, True)
        elif self.orientation == "left":
            self.image = pg.transform.rotate(texture, 90)

class Weapon(UpgradeSlot):
    def __init__(self, 
                 pos: tuple[int, int], 
                 orientation: str,
                 weapon_id: str,
                 sprite_group: pg.sprite.Group,
                 ) -> None:

        # textures
        self._txt_set = textures["weaponry"][weapon_id]
        self._anim_idle = self._txt_set["disabled"]
        self._anim_charge = [frame for frame in self._txt_set["charging"]]
        self._anim_ready = self._txt_set["ready"]

        # logic

        self.req_power = weapons[weapon_id]["req_power"]
        self.charge_time = 0
        self.charge_diff = 1
        self.curr_charge = 0
        self.weapon_name = weapon_id
        self.display_name = weapons[weapon_id]["name"]
        self.state = "disabled" # disabled | charging | ready
        UpgradeSlot.__init__(self, pos, orientation, self._anim_idle, sprite_group)
    
    def activate(self) -> None:
        """
        Activate the weapon. (set it's state to charging)
        """
        self.state = "charging"
        self.curr_charge = 0

    def disable(self) -> None:
        """
        Disable the weapon.
        """
        self.change_texture(self._anim_idle)
        self.state = "disabled"

    def update(self) -> None: # TODO: implement charge time
        """
        Update the weapon's state.
        """
        if self.state == "charging":
            self.change_texture(self._anim_charge[self.curr_charge])
            self.curr_charge += self.charge_diff

            if self.curr_charge >= self.charge_time:
                self.state = "ready"
                self.change_texture(self._anim_ready)
        elif self.state == "ready":
            self.change_texture(self._anim_ready)
        elif self.state == "disabled":
            self.curr_charge -= self.charge_diff # slowly decrease the charge
            self.change_texture(self._anim_idle)

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