from __future__ import annotations
from typing import TYPE_CHECKING, Union, Literal
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.room import Room

from modules.resources import textures, weapons
from modules.projectile import Projectile

class UpgradeSlot(pg.sprite.Sprite):
    # public
    purpose: Literal["weapon", "thruster", "shield"]
    orientation: Literal["top", "right", "bottom", "left"]
    image: pg.Surface
    pos: tuple[int, int]
    rect: pg.Rect

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
    # public
    charge_speed: int
    curr_charge: int
    projectile_queue: list[Projectile]
    state: Literal["disabled", "charging", "ready"]

    weapon_name: str
    display_name: str
    req_power: int
    charge_time: int
    volley_shots: int
    volley_delay: float
    projectile_type: Literal["laser", "missile", "beam"]

    # private
    _txt_set: dict[str, dict[str, pg.Surface]]
    _anim_idle: pg.Surface  
    _anim_charge: list[pg.Surface]
    _anim_ready: pg.Surface

    _target: Union[Room, None]

    def __init__(self, 
                 pos: tuple[int, int], 
                 orientation: Literal["top", "right", "bottom", "left"],
                 weapon_id: str,
                 sprite_group: pg.sprite.Group
                 ) -> None:

        # textures
        self._txt_set = textures["weaponry"][weapon_id]
        self._anim_idle = self._txt_set["disabled"]
        self._anim_charge = [frame for frame in self._txt_set["charging"]]
        self._anim_ready = self._txt_set["ready"]

        # logic
        self._target = None
        self.charge_speed = 15
        self.curr_charge = 0
        self.projectile_queue = [] # list of projectiles to be fired
        self.state = "disabled"

        self.weapon_name = weapon_id
        self.display_name = weapons[weapon_id]["name"]
        self.req_power = weapons[weapon_id]["req_power"]
        self.charge_time = weapons[weapon_id]["charge_time"]
        self.volley_shots = weapons[weapon_id]["volley_shots"]
        self.volley_delay = weapons[weapon_id]["volley_delay"]
        self.projectile_type = weapons[weapon_id]["projectile_type"]

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

    def update(self, dt) -> None:
        """
        Update the weapon's state and fire queued projectiles.
        """
        if self.state == "charging":
            if self.curr_charge >= self.charge_time:
                self.state = "ready"
                self.change_texture(self._anim_ready)

            anim_charge_len = len(self._anim_charge)
            anim_charge_index = int(self.curr_charge // (self.charge_time // anim_charge_len)) # + 1 is to account for floating point errors (it could break in the future)
            if anim_charge_index > len(self._anim_charge) - 1:
                anim_charge_index = len(self._anim_charge) - 1

            self.change_texture(self._anim_charge[anim_charge_index])
            self.curr_charge += round(self.charge_speed * dt, 2)
        elif self.state == "disabled":
            self.curr_charge -= round(self.charge_speed * dt, 2) # slowly decrease the charge

            anim_charge_len = len(self._anim_charge)
            anim_charge_index = int((self.curr_charge) // (self.charge_time // anim_charge_len)) 
            if anim_charge_index > len(self._anim_charge) - 1:
                anim_charge_index = len(self._anim_charge) - 1

            self.change_texture(self._anim_charge[anim_charge_index])

            if self.curr_charge <= 0:
                self.curr_charge = 0
                self.change_texture(self._anim_idle)
        elif self.state == "ready":
            self.change_texture(self._anim_ready)
            
        for projectile in self.projectile_queue:
            if projectile.hit_target:
                self.projectile_queue.remove(projectile)
    
    def fire(self, first_pos: tuple[int, int], target_room: Room) -> tuple[Projectile]:
        """
        Fire the weapon.
        """
        if self.state == "ready":
            self.state = "charging"
            self.curr_charge = 0

        for i in range(self.volley_shots):
            delay = self.volley_delay * i
            projectile = Projectile(self.rect.center, first_pos, self.projectile_type, 1, 300, (255,0,0), 15, 3, delay, target_room, not target_room.parent.enemy)
            self.projectile_queue.append(projectile)

        return self.projectile_queue

    def __str__(self) -> str:
        """Return the name of the weapon."""
        return self.display_name

    def __bool__(self) -> bool:
        """Return True if the weapon is ready to fire."""
        return self.state == "ready"

    @property
    def target(self) -> Union[Room, None]:
        """
        Return the target of the weapon.
        :return: Room - the target room
        """
        return self._target

    @target.setter
    def target(self, room: Union[Room, None]) -> None:
        """
        Set the target of the weapon.
        :param room: Room - the target room
        """
        if room is not None:
            self._target = room
            self._target.targeted_by.append(self)
        else:
            self._target.targeted_by.remove(self) if self._target is not None else None
            self._target = None

class Thruster(UpgradeSlot):
    # public
    thruster_type: str

    # private
    _txt_set: dict[str, pg.Surface]
    _anim_idle: pg.Surface
    _anim_active: pg.Surface

    def __init__(self, 
                 pos: tuple[int, int], 
                 orientation: str,
                 thruster_type: str,
                 sprite_group: pg.sprite.Group,
                 ) -> None:
        
        self.thruster_type = thruster_type
        self._txt_set = textures["thrusters"][thruster_type]
        self._anim_idle = self._txt_set["idle"]
        self._anim_active = self._txt_set["active"]

        UpgradeSlot.__init__(self, pos, orientation, self._anim_idle, sprite_group)

class Shield(UpgradeSlot):
    # public
    pos: tuple[int, int]
    realpos: tuple[int, int]
    shield_image: pg.Surface
    shield_sprite: pg.sprite.Sprite
    shield_mask: pg.mask.Mask

    charge: int
    max_charge: int
    charge_time: int
    charge_change: int
    # private

    def __init__(self, 
                 pos: tuple[int, int], 
                 realpos: tuple[int, int],
                 orientation: Literal["top", "right", "bottom", "left"],
                 shield_id: str,
                 shield: pg.sprite.Sprite,
                 sprite_group: pg.sprite.Group,
                 ship_corners: tuple[tuple[int, int], tuple[int, int]],
                 ) -> None:
        """
        :param pos: tuple[int, int] - the relative position of the upgrade slot
        :param realpos: tuple[int, int] - the absolute position of the upgrade slot
        :param role: str - the role of the upgrade slot
        :param ship_corners: tuple[tuple[int, int], tuple[int, int]] - the corners of the ship (top-left, bottom-right)
        """
        UpgradeSlot.__init__(self, pos, orientation, textures["shield_upgrades"][shield_id], sprite_group)
        self.shield_sprite = shield

        self.pos = pos
        self.realpos = realpos

        # shield logic
        self.charge = 0
        self.curr_charge = 0.0
        self.max_charge = 0
        self.charge_time = 100
        self.charge_change = 25

    def post_init_update(self, ship_corners: tuple[tuple[int, int], tuple[int, int]], ship_center: tuple[int, int]) -> None:
        """
        Update the shield's position and hitbox.
        :param ship_corners: tuple[tuple[int, int], tuple[int, int]] - the corners of the ship (top-left, bottom-right)
        :param ship_center: tuple[int, int] - the center of the ship
        """
        
        width = ship_corners[1][0] - ship_corners[0][0]
        height = ship_corners[1][1] - ship_corners[0][1]
        
        self.shield_sprite.image = pg.transform.scale(self.shield_sprite.image, (width+144, height+144))
        self.shield_sprite.rect = self.shield_sprite.image.get_rect(center=ship_center)
        self.shield_mask = pg.mask.from_surface(self.shield_sprite.image, threshold=0)
        # TODO: above funtion's threshold parameter creates a mask that doesn't always match the sprite's alpha channel
        
    def draw(self, screen: pg.Surface) -> None:
        if hasattr(self, "shield_sprite") and self.charge > 0:
            screen.blit(self.shield_sprite.image, self.shield_sprite.rect)

            # uncomment to draw the shield's mask
            #screen.blit(self.shield_mask.to_surface(setcolor=(0,255,0,125,)), self.shield_sprite.rect.topleft)

    def update(self, dt: float, max_charge: int) -> None:
        """
        Update the shield's charge.
        :param dt: float - the time since the last frame
        """
        self.max_charge = max_charge
        
        if self.charge < self.max_charge:
            self.curr_charge += dt * self.charge_change

            if self.curr_charge >= self.charge_time:
                self.charge += 1
                self.curr_charge = 0
        elif self.charge > self.max_charge:
            self.charge = self.max_charge

        return

    def take_damage(self, projectile: Projectile) -> None:
        """
        Take damage from a projectile.
        :param projectile: Projectile - the projectile that hit the shield
        """

        if projectile.type == "beam": # beams don't deal damage to shields
            return 
        else:
            self.charge -= 1

        return