from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.room import Projectile
    from modules.spaceship.spaceship import Spaceship

from modules.spaceship.tile import Tile
from modules.spaceship.upgrades import *
from modules.resources import textures, GameEvents

class Room(pg.sprite.Group):
    # public
    rect: pg.Rect
    hitbox: pg.Rect

    pos: tuple[int, int]
    room_layout: list[list[int]]
    room_tile_layout: list[list[Tile]]
    adjecent_rooms: dict[Room, tuple[Tile, Tile]]
    parent: Spaceship
    role: Union[str, None]
    level: int
    icon: Union[pg.Surface, None]

    selected: bool
    hovering: bool
    occupied: bool

    aimed_at: bool
    targeted_by: list[Weapon]

    repair_progress: float

    # private
    _upgrade_index: int
    _enemy_ship: bool
    _power: int 
    _health: int

    def __init__(self, 
                 pos: tuple[int, int],
                 realpos: tuple[int, int],
                 room_layout: list[list[int]],
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
            self.hitbox = pg.Rect(realpos, (self.rect.width, self.rect.height)[::-1])
        else:
            self.hitbox = pg.Rect(realpos, (self.rect.width, self.rect.height))
    
        self.pos = pos
        self.room_layout = room_layout
        self.room_tile_layout = list()
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

        self.repair_progress = 0

        for x, collumn in enumerate(self.room_layout):
            col = list()
            for y, tile in enumerate(collumn):
                tile = Tile(self.pos, (x, y), self)
                self.add(tile)
                col.append(tile)
            self.room_tile_layout.append(col)

        for upgrade_type in upgrade_slots:
            for orientation in upgrade_slots[upgrade_type]:
                self.place_upgrade(upgrade_type, orientation, upgrade_slots[upgrade_type][orientation])
        
        # check if the room has a role (is a system room)
        self.role = role if role is not None else None
        self.level = level if level is not None else 0
        self.icon = None
        if self.role is not None:
            self.icon = textures["system_icons"][self.role]["overlayGrey"]
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
            screen.blit(self.icon.image, 
                        (self.rect.centerx-(self.icon.image.get_width()/2), 
                         self.rect.centery-(self.icon.image.get_height()/2))
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
        
        # draw the targeted outline only if player ship has sensors above power level 2
        if ((not self._enemy_ship and self.parent.installed_systems["sensors"].power >= 2) or self._enemy_ship) and len(self.targeted_by) > 0:
            pg.draw.rect(screen, (125,0,0,255), self.rect.inflate(-4, -4), 1)
            pg.draw.rect(screen, (125,0,0,150), self.rect.inflate(-8, -8), 1)

    def place_upgrade(self, upgrade_type: str, orientation: str, upgrade_name: str) -> None:
        """
        Place an upgrade slot or a specified weapon in the given slot.
        :param upgrade_type: str - the type of upgrade slot
        :param orientation: str - the orientation of the upgrade slot
        :param upgrade_name: str - the name of the upgrade
        """
        
        # find the position of the upgrade slot
        upgrade_pos = None
        upgrade_realpos = None

        match orientation:
            case "top":
                upgrade_pos = (self.rect.centerx, self.rect.y)
                upgrade_realpos = (self.hitbox.centerx, self.hitbox.y)
            case "right":
                upgrade_pos = (self.rect.right, self.rect.centery)
                upgrade_realpos = (self.hitbox.right, self.hitbox.centery)
            case "bottom":
                upgrade_pos = (self.rect.centerx, self.rect.bottom)
                upgrade_realpos = (self.hitbox.centerx, self.hitbox.bottom)
            case "left":
                upgrade_pos = (self.rect.x, self.rect.centery)
                upgrade_realpos = (self.hitbox.x, self.hitbox.centery)
        
        # create the correct upgrade slot type
        if upgrade_name is None:
            self.upgrade_slots[self._upgrade_index] = UpgradeSlot(upgrade_pos, orientation, textures["upgrade_slot"], self, upgrade_type)
        elif upgrade_name in textures["weaponry"]:
            self.upgrade_slots[self._upgrade_index] = Weapon(upgrade_pos, orientation, upgrade_name, self)
        elif upgrade_name in textures["thrusters"]:
            self.upgrade_slots[self._upgrade_index] = Thruster(upgrade_pos, orientation, upgrade_name, self)
        elif upgrade_name in textures["shield_upgrades"]:
            sprite = pg.sprite.Sprite()
            sprite.image = textures["shields"]["enemyShield"].image.copy()
            sprite.rect = sprite.image.get_rect()

            new_shield = Shield(upgrade_pos, upgrade_realpos, orientation, upgrade_name, sprite, self, self.parent.get_corners())
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
        self.parent.event_queue.append(GameEvents.TOOK_DAMAGE)

        # TODO: implement projectile type specific damage
        if hasattr(self, "_health"):
            self.health_points -= projectile.damage

        return

    def get_random_tile(self) -> Union[Tile, None]:
        """
        Return a random tile from the room or None if all are occupied.
        :return: Union[Tile, None] - the random tile
        """

        for sprite in self.sprites():
            if isinstance(sprite, Tile) and not sprite.occupied:
                return sprite
        
        # no free tile was found
        return None

    def check_hover(self, mouse_pos: tuple[int, int]) -> None:
        # TODO: highlight tiles if the mouse is hovering over the room
        return
    
    def check_clicked(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[bool, bool, bool]) -> Union[Tile, None]:
        """
        Check if the room is clicked and select it if it is.
        :param mouse_pos: tuple[int, int] - the current mouse position
        :param mouse_clicked: tuple[bool, bool, bool] - the current state of the mouse buttons
        """
        if not mouse_clicked[2]:
            return

        for tile in self.sprites():
            if isinstance(tile, Tile):
                if tile.selected == False and tile.occupied == False and tile.hitbox.collidepoint(mouse_pos):
                    return tile

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
                case "weapons" | "thrusters" | "medbay" | "oxygen" | "engines" | "pilot" | "sensors":
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
            # shield power usage is doubled
            change = value - self._power

            # check if power can be assigned:
            if (value >=0 and # power is not negative
                value <= self.max_power and # power is not higher than the max power
                self.parent.usable_power >= value - self.power and # enough power is available
                self.health_points >= (self._power + (change*2) if self.role == "shields" else value) # enough health points are available
                ):

                self._power += change * 2 if self.role == "shields" else change

                if self.role == "shields":
                    if self.parent.installed_shield is not None and self.parent.installed_shield.curr_charge > 0:
                        self.parent.installed_shield.curr_charge = 0 if self._power == 0 else self.parent.installed_shield.curr_charge
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
                # if the room is a weapons room disable weapons using more power than the health points
                if self.role == "weapons" and value < self._health and self.power >= self._health:
                    for weapon in self.parent.weapons:
                        if self.power > value and weapon.state != "disabled":
                            weapon.disable()
                            self.power -= weapon.req_power
                        elif self.power <= value:
                            break

                # the power level can't be higher than the health points
                elif value < self._health and self.power >= self._health:
                    self.power = value

                self._health = value

                if self._health == self.max_power: # normal
                    self.icon = textures["system_icons"][self.role]["overlayGrey"]

                elif self._health < self.max_power and self._health > 0: # damaged
                    self.icon = textures["system_icons"][self.role]["overlayOrange"]

                else: # destroyed
                    self.icon = textures["system_icons"][self.role]["overlayRed"]

        return
    
    @property
    def needs_repair(self) -> bool:
        """Return True if the room needs repair, else False."""

        if hasattr(self, "_health") and self.role is not None:
            return self._health < self.max_power
        return False

    @property
    def icon(self) -> Union[pg.Surface, None]:
        """Return the icon of the room. (If the room is a system room, else return None)"""

        if hasattr(self, "_icon"):
            return self._icon
        return None
    
    @icon.setter
    def icon(self, icon: pg.sprite.Sprite) -> None:
        """
        Set the icon of the room.
        :param icon: pg.sprite.Sprite - the new icon
        """

        if icon is not None:
            if self._enemy_ship:
                self._icon = pg.sprite.Sprite()
                self._icon.image = icon.image.copy()
                self._icon.image = pg.transform.rotate(self._icon.image, 270)
                self._icon.rect = self._icon.image.get_rect()
            else:
                self._icon = icon
        return
