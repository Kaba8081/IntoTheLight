from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.door import Door
    from modules.spaceship.room import Room
    from modules.spaceship.upgrades import *

from modules.spaceship.spaceship import Spaceship
from modules.resources import keybinds

class Player(Spaceship):
    # public
    enemy: bool
    fuel: int
    missles: int
    drones: int
    scrap: int
    selected_weapon: Union[Weapon, None]

    enemy = False
    
    def __init__(self, 
                 ship_type: str = "scout",
                 screen_size: tuple[int, int] = (800, 600)
                 ) -> None:
        
        # additional player data
        self.fuel = 16
        self.missles = 8
        self.drones = 2
        self.scrap = 10

        # weapon logic
        self.selected_weapon = None

        super().__init__(ship_type, screen_size)
    
    def update(self, dt: float, mouse_pos: tuple[int, int], mouse_btns: tuple[bool,bool,bool]  = None) -> None:
        """
        Update the player's components.
        :param dt: float - the time since the last frame
        :param mouse_pos: tuple[int, int] - the current mouse position
        :param mouse_clicked: tuple[bool, bool, bool] - the current state of the mouse buttons
        """
        super().update(dt)

        # check if the player clicked / is hovering on a door
        door: Door
        for door in self.doors:
            if door.rect.collidepoint(mouse_pos):
                door.hovering = True
                if mouse_btns is not None and mouse_btns[0]:
                    door.toggle()

    def key_pressed(self, key: pg.key) -> None:
        """Handles player input from the keyboard."""
        # TODO: definetly can be improved

        num_of_weapons = len(self.weapons)

        if key == keybinds["select_weapon1"] and num_of_weapons >= 1:
            if self.weapons[0].state == "disabled": # activate the weapon if it's disabled
                self.selected_weapon = self.weapons[0] if self.activate_weapon(self.weapons[0]) else None
            else:
                self.selected_weapon = self.weapons[0]
                self.selected_weapon.target = None
        if key == keybinds["select_weapon2"] and num_of_weapons >= 2:
            if self.weapons[1].state == "disabled": # activate the weapon if it's disabled
                self.selected_weapon = self.weapons[1] if self.activate_weapon(self.weapons[1]) else None
            else:
                self.selected_weapon = self.weapons[1]
                self.selected_weapon.target = None
        if key == keybinds["select_weapon3"] and num_of_weapons >= 3:
            if self.weapons[2].state == "disabled": # activate the weapon if it's disabled
                self.selected_weapon = self.weapons[2] if self.activate_weapon(self.weapons[2]) else None
            else:
                self.selected_weapon = self.weapons[2]
                self.selected_weapon.target = None
        if key == keybinds["select_weapon4"] and num_of_weapons >= 4:
            if self.weapons[3].state == "disabled": # activate the weapon if it's disabled
                self.selected_weapon = self.weapons[3] if self.activate_weapon(self.weapons[3]) else None
            else:
                self.selected_weapon = self.weapons[3]
                self.selected_weapon.target = None
        
        return
    
    def toggle_autofire(self) -> bool:
        """Toggles the autofire state of the player's weapons."""
        self.autofire = not self.autofire
        return self.autofire