from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.room import Projectile
    from modules.spaceship.spaceship import Spaceship

from modules.spaceship.tile import Tile
from modules.spaceship.upgrades import *
from modules.resources import textures

class Room(pg.sprite.Group):
    # public
    rect: pg.Rect
    hitbox: pg.Rect

    pos: tuple[int, int]
    room_layout: list[dict]
    adjecent_rooms: dict[Room, list[tuple[int, int]]]
    parent: Spaceship
    role: Union[str, None]
    level: int
    icon: Union[pg.Surface, None]

    selected: bool
    hovering: bool

    aimed_at: bool
    targeted_by: list[Weapon]

    # private
    _upgrade_index: int
    _enemy_ship: bool
    _power: int 
    _health: int

    _icon_preset: pg.Surface
    _icon_color_stable = (105, 106, 106)
    _icon_color_damaged = (249,163,27)
    _icon_color_destroyed = (180, 32, 42)

    def __init__(self, 
                 pos: tuple[int, int],
                 realpos: tuple[int, int],
                 room_layout: list[dict],
                 parent: Spaceship,
                 upgrade_slots: dict[str, str] = {},
                 role: str = None,
                 level: int = None,
                 enemy_ship: bool = False,
                 ) -> None:
        
        pg.sprite.Group.__init__(self)
        self.rect = pg.Rect(
            (pos[0], pos[1]), 
            (len(room_layout)*32, len(room_layout[0])*32))
        if enemy_ship:
            self.hitbox = pg.Rect((realpos[1],realpos[0]), (self.rect.height, self.rect.width))
        else:
            self.hitbox = pg.Rect(realpos, (self.rect.width, self.rect.height))
    
        self.pos = pos
        self.room_layout = room_layout
        self.adjecent_rooms = {}
        self.upgrade_slots = {}
        self.parent = parent
        self._upgrade_index = 0
        self._enemy_ship = enemy_ship

        # player interaction
        self.selected = False
        self.hovering = False

        # enemy ship
        self.aimed_at = False
        self.targeted_by = []

        for x, collumn in enumerate(self.room_layout):
            for y, tile in enumerate(collumn):
                tile = Tile(self.pos, (x, y), textures["tile_default"], self)
                self.add(tile)

        for upgrade_type in upgrade_slots:
            for orientation in upgrade_slots[upgrade_type]:
                self.place_upgrade(upgrade_type, orientation, upgrade_slots[upgrade_type][orientation])
        
        # check if the room has a role (is a system room)
        self.role = role if role is not None else None
        self.level = level if level is not None else 0
        self.icon = None
        if self.role is not None:
            self._icon_preset = textures[self.role]
            self._icon_preset = pg.transform.rotate(self._icon_preset, 270) if enemy_ship else self._icon_preset
            self.icon = self._icon_preset.__copy__()
            self._power = 0
            self._health = self.max_power

    def update(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[bool, bool, bool]) -> None:
        """
        Update the room's state based on the mouse position and click event.
        :param mouse_pos: tuple[int, int] - the current mouse position
        :param mouse_clicked: tuple[bool, bool, bool] - the current state of the mouse buttons
        """

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
    
        return

    def draw(self, screen: pg.surface.Surface) -> None:
        """
        Draw the room and it's components on the screen.
        :param screen: pg.surface.Surface - the screen to draw on
        """

        sprites = self.sprites()

        # draw all sprites in the room
        for spr in sprites:
            self.spritedict[spr] = screen.blit(spr.image, spr.rect)

        pg.draw.rect(screen, (89,86,82), self.rect, 2)

        # draw icon if the room has a role
        if self.icon is not None:
            screen.blit(self.icon, 
                        (self.rect.centerx-(self.icon.get_width()/2), 
                         self.rect.centery-(self.icon.get_height()/2))
                        )
        
        # darken the room if selected or hovering
        if self.selected: 
            s = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA) 
            s.fill((0,0,0,128))
            screen.blit(s, self.rect)

        elif self.hovering:
            s = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA) 
            s.fill((0,0,0,64)) 
            screen.blit(s, self.rect)
        
        # draw a red border if the room is being targeted
        if self.aimed_at:
            pg.draw.rect(screen, (255,0,0,255), self.rect.inflate(-4, -4), 1)
            pg.draw.rect(screen, (255,0,0,150), self.rect.inflate(-8, -8), 1)
            pg.draw.rect(screen, (255,0,0,75), self.rect.inflate(-10, -10), 1)
        
        if len(self.targeted_by) > 0:
            pg.draw.rect(screen, (125,0,0,255), self.rect.inflate(-4, -4), 1)
            pg.draw.rect(screen, (125,0,0,150), self.rect.inflate(-8, -8), 1)

    def move_by_distance(self, distance: tuple[int, int]) -> None:
        self.rect.x += distance[0]
        self.rect.y += distance[1]

        for tile in self.sprites():
            tile.rect.x += distance[0]
            tile.rect.y += distance[1]
        
        distance = distance[::-1] if self._enemy_ship else distance # flip axises if enemy ship
        self.hitbox.x += distance[0]
        self.hitbox.y += distance[1]

    def place_upgrade(self, upgrade_type: str, orientation: str, upgrade_name: str) -> None:
        """
        Place an upgrade slot or a specified weapon in the given slot.
        :param upgrade_type: str - the type of upgrade slot
        :param orientation: str - the orientation of the upgrade slot
        :param upgrade_name: str - the name of the upgrade
        """
        
        # find the position of the upgrade slot
        upgrade_pos = None

        match orientation:
            case "top":
                upgrade_pos = (self.rect.centerx, self.rect.y)
            case "right":
                upgrade_pos = (self.rect.right, self.rect.centery)
            case "bottom":
                upgrade_pos = (self.rect.centerx, self.rect.bottom)
            case "left":
                upgrade_pos = (self.rect.x, self.rect.centery)
        
        # create the correct upgrade slot type
        if upgrade_name is None:
            self.upgrade_slots[self._upgrade_index] = UpgradeSlot(upgrade_pos, orientation, textures["upgrade_slot"], self, upgrade_type)
        elif upgrade_name in textures["weaponry"]:
            self.upgrade_slots[self._upgrade_index] = Weapon(upgrade_pos, orientation, upgrade_name, self)
        elif upgrade_name in textures["thrusters"]:
            self.upgrade_slots[self._upgrade_index] = Thruster(upgrade_pos, orientation, upgrade_name, self)
        elif upgrade_name in textures["shield_upgrades"]:
            new_shield = Shield(upgrade_pos, (0,0), orientation, upgrade_name, self, self.parent.get_corners())
            self.upgrade_slots[self._upgrade_index] = new_shield
            self.parent.installed_shield = new_shield
        else: # invalid upgrade name
            self.upgrade_slots[self._upgrade_index] = UpgradeSlot(upgrade_pos, orientation, textures["upgrade_slot"], self, upgrade_type)
        
        self._upgrade_index += 1

        return

    def take_damage(self, projectile: Projectile) -> None:
        """
        Take damage to the room.
        :param projectile: Projectile - the projectile that hit the room
        """

        self.parent.hull_hp -= projectile.damage

        # TODO: implement projectile type specific damage
        if hasattr(self, "_health"):
            self.health_points -= projectile.damage

        return

    def dev_draw_hitbox(self, screen: pg.surface.Surface) -> None:
        """
        Draw the hitbox of the room for debugging.
        :param screen: pg.surface.Surface - the screen to draw on
        """
        pg.draw.rect(screen, (0,255,0, 50), self.hitbox)

    @property
    def empty_upgrade_slots(self) -> Union[list[UpgradeSlot], None]:
        empty_slots = []
        for slot in self.upgrade_slots:
            if isinstance(self.upgrade_slots[slot], UpgradeSlot):
                empty_slots.append(self.upgrade_slots[slot])

        return empty_slots if len(empty_slots) > 0 else None

    @property
    def weapons(self) -> Union[list[Weapon], None]:
        weapons = []
        for slot in self.upgrade_slots:
            if isinstance(self.upgrade_slots[slot], Weapon):
                weapons.append(self.upgrade_slots[slot])
        
        return weapons if len(weapons) > 0 else None
    
    @property
    def thrusters(self) -> Union[list[Thruster], None]:
        thrusters = []
        for slot in self.upgrade_slots:
            if isinstance(self.upgrade_slots[slot], Thruster):
                thrusters.append(self.upgrade_slots[slot])
        
        return thrusters if len(thrusters) > 0 else None

    @property
    def max_power(self) -> int:
        """Return the maximum power that can be used in the room."""

        try:
            if self.level is None or self.role is None:
                raise AttributeError
            match self.role:
                # rooms where the power level is the same as the room level
                case "weapons" | "thrusters" | "medbay" | "o2" | "engines" | "bridge" | "cameras":
                    return self.level
                
                case "shields":
                    return self.level * 2
                
                # room has no or unknown role
                case _:
                    raise ValueError
        except ValueError:
            print("Could not return max_power: Room is not a system room!")
            return 0
        except AttributeError:
            print("Could not return max_power: Room level or role has not been set!")
            return 0

    @property
    def power(self) -> int:
        """Return the current power used in the room."""

        if hasattr(self, "_power") and self.role is not None:
            return self._power
        else:
            print("Could not return max_power: Room is not a system room or _power has not been set!")
            return 0
        
    @power.setter
    def power(self, value: int) -> None:
        """
        Set the power level of the room.
        :param value: int - the new power level
        """

        if hasattr(self, "_power") and self.role is not None:
            if value >=0 and value <= self.max_power:
                self._power = value
            else:
                print(f"Could not set power: Power level is out of range! (role: {self.role}, {value}/{self.max_power})")
        else:
            print("Could not set power: Room is not a system room!")

        return

    @property
    def health_points(self) -> Union[int, None]:
        """Return the current health points of the room. (If the room is a system room, else return None)"""

        if hasattr(self, "_health") and self.role is not None:
            return self._health
        return None
    
    @health_points.setter
    def health_points(self, value: int) -> None:
        """
        Set the health points of the room.
        :param value: int - the new health points
        """

        if hasattr(self, "_health") and self.role is not None:
            if value >= 0 and value <= self.max_power:
                self._health = value

                if self._health == self.max_power: # normal
                    self.icon = self._icon_preset

                elif self._health < self.max_power and self._health > 0: # damaged
                    pg.transform.threshold(self.icon, self._icon_preset, self._icon_color_stable, (0,0,0,0), self._icon_color_damaged, inverse_set=True)

                else:
                    pg.transform.threshold(self.icon, self._icon_preset, self._icon_color_stable, (0,0,0,0), self._icon_color_destroyed, inverse_set=True)

        return