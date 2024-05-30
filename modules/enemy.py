from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.upgrades import *

from modules.spaceship.spaceship import Spaceship
from modules.spaceship.room import Room

from random import randint

# systems ordered by priority
enemy_weapon_targets = [
    "weapons",
    "shields",
    "engines",
    "oxygen",
    "medbay",
    "pilot",
    "sensors",
    "drones",
    "doors"
]

class Enemy(Spaceship):
    # public 
    hull_hp: int
    
    enemy = True

    def __init__(self, 
                 ship_type: str = "cruiser",
                 screen_size: tuple[int, int] = (800, 600),
                 offset: tuple[int, int] = (0,0),
                 ) -> None:
        super().__init__(ship_type, screen_size, True, offset)

        self.hull_hp = randint(12,20)

        for system in self.installed_systems.values():
            print(system.role, system.power)
    
    def select_room(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[bool, bool, bool]) -> Union[Room, None]:
        """
        Select a room if the cursor is hovering over it.
        :param mouse_pos: tuple[int, int] The current mouse position.
        :param mouse_clicked: tuple[bool, bool, bool] The current state of the mouse buttons.
        :return: Union[Room, None] The selected room or None if no room was found.
        """
        if self.destroyed:
            return None

        for room in self.rooms:
            room.aimed_at = False
            if room.hitbox.collidepoint(mouse_pos):
                # TODO: Add an icon to show that the room is being targeted
                return room
        
        return None

    def hover_weapon(self, mouse_pos: tuple[int, int]) -> None:
        """
        Highlight the room if the cursor is hovering over it.
        """
        if self.destroyed:
            return

        for room in self.rooms:
            room.aimed_at = False
            if room.hitbox.collidepoint(mouse_pos):
                room.aimed_at = True
        
        return
    
    def check_weapon_states(self, enemy_ship: Spaceship) -> None:
        """Updates the state of enemy weapons"""
        # checks if every weapon is active, if not, try to activate it
        for weapon in self.weapons:
            if weapon.state == "disabled":
                self.activate_weapon(weapon)

        # checks if every active weapon has a target assigned
        for weapon in self.weapons:
            if not weapon.state == "disabled" and not weapon.target:
                while True:
                    random_system = enemy_weapon_targets[randint(0, len(enemy_weapon_targets)-1)]
                    if random_system in enemy_ship.installed_systems.keys():
                        weapon.target = enemy_ship.installed_systems[random_system]
                        break
        
        return

    @property
    def max_power(self) -> int: # TODO: implement enemy power manegement
        """Return the maximum power that the ship generates."""

        # For now the enemy ship has a fixed power level
        return 100