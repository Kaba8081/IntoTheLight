import pygame as pg
from os import path
from typing import Union

from modules.spaceship.tile import Tile
from modules.spaceship.upgrades import *
from modules.resources import textures

class Room(pg.sprite.Group):
    def __init__(self, 
                 pos: tuple[int, int], 
                 room_layout: list,
                 upgrade_slots: dict[str, str] = {},
                 role: str = None,
                 level: int = None,
                 enemy_ship: bool = False,
                 ) -> None:
        
        pg.sprite.Group.__init__(self)
        self.rect = pg.Rect(
            (pos[0]*32, pos[1]*32), 
            (len(room_layout)*32, len(room_layout[0])*32))
        
        self.pos = pos
        self.room_layout = room_layout
        self.adjecent_rooms = {} # room class : connected tiles
        self.upgrade_slots = {}
        self._upgrade_index = 0

        self.selected = False
        self.hovering = False

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
            self.icon = textures[self.role]
            self.icon = pg.transform.rotate(self.icon, 270) if enemy_ship else self.icon
            self._power = 0

    def update(self, mouse_pos: tuple[int, int], mouse_clicked: bool) -> None:
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

    def draw(self, screen) -> None:
        sprites = self.sprites()

        # draw all sprites in the room
        for spr in sprites:
            self.spritedict[spr] = screen.blit(spr.image, spr.rect)
        
        # draw room outline
        pg.draw.lines(
            screen, 
            (89,86,82), 
            True, 
            [
                # top left -> top right 
                (self.rect.x, self.rect.y),
                (self.rect.x+self.rect.width, self.rect.y), 
                # top right -> bottom right
                (self.rect.x+self.rect.width, self.rect.y), 
                (self.rect.x+self.rect.width, self.rect.y+self.rect.height),
                # bottom right -> bottom left
                (self.rect.x+self.rect.width, self.rect.y+self.rect.height),
                (self.rect.x, self.rect.y+self.rect.height),
                # bottom left -> top left
                (self.rect.x, self.rect.y+self.rect.height),
                (self.rect.x, self.rect.y)
            ],
            4
        )

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
    
    def place_upgrade(self, upgrade_type: str, orientation: str, upgrade_name: str) -> None:
        """Place an upgrade slot or a specified weapon in the given slot."""
        
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
        else: # invalid upgrade name
            self.upgrade_slots[self._upgrade_index] = UpgradeSlot(upgrade_pos, orientation, textures["upgrade_slot"], self, upgrade_type)
        
        self._upgrade_index += 1

        return
    
    @property
    def empty_upgrade_slots(self) -> Union[list, None]:
        empty_slots = []
        for slot in self.upgrade_slots:
            if isinstance(self.upgrade_slots[slot], UpgradeSlot):
                empty_slots.append(self.upgrade_slots[slot])

        return empty_slots if len(empty_slots) > 0 else None

    @property
    def weapons(self) -> Union[list, None]:
        weapons = []
        for slot in self.upgrade_slots:
            if isinstance(self.upgrade_slots[slot], Weapon):
                weapons.append(self.upgrade_slots[slot])
        
        return weapons if len(weapons) > 0 else None
    
    @property
    def thrusters(self) -> Union[list, None]:
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