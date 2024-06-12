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

        self.hull_hp = randint(6,20)
    
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
        :param mouse_pos: tuple[int, int] The current mouse position.
        """
        if self.destroyed:
            return

        for room in self.rooms:
            room.aimed_at = False
            if room.hitbox.collidepoint(mouse_pos):
                room.aimed_at = True
        
        return
    
    def check_weapon_states(self, enemy_ship: Spaceship) -> None:
        """
        Updates the state of enemy weapons
        :param enemy_ship: Spaceship - the player's ship
        """
        if enemy_ship.destroyed:
            return

        # checks if every weapon is active, if not, try to activate it
        for weapon in self.weapons:
            if weapon.state == "disabled":
                self.activate_weapon(weapon)

        for weapon in self.weapons:
            # checks if every active weapon has a target assigned
            if not weapon.state == "disabled" and not weapon.target:
                weapon.target = self._target_enemy_room(enemy_ship)
                    
        return
    
    def _target_enemy_room(self, enemy_ship: Spaceship) -> Room:
        """Select a room to target on the enemy ship."""

        for system in enemy_weapon_targets:
            if system in enemy_ship.installed_systems.keys():
                # if the target room is destroyed, continue to the next one
                if enemy_ship.installed_systems[system].health_points == 0:
                    continue
                
                # if the target room's hp is below max, there is a 70% to find a diffrent room
                elif enemy_ship.installed_systems[system].health_points < enemy_ship.installed_systems[system].max_power:
                    if randint(0, 100) > 70:
                        continue

                return enemy_ship.installed_systems[system]
        
        # if all systems were skipped just pick a random one
        random_system = list(enemy_ship.installed_systems.values())[randint(0, len(enemy_ship.installed_systems)-1)]
        return random_system

    def manage_power(self) -> None:
        """Try to activate systems based on the power level."""
        while True:
            for system in self.installed_systems.keys():
                if not self.check_if_system_accepts_power(system, 2 if system=="shields" else 1):
                    return
                self.installed_systems[system].power += 1

    @property
    def max_power(self) -> int: # TODO: implement enemy power manegement
        """Return the maximum power that the ship generates."""

        # For now the enemy ship has a fixed power level
        return 100