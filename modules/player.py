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

    def toggle_system_power(self, action: tuple[str, bool], value: int = 1) -> None:
        """ 
        Toggles the power level of a system. 

        :param action: tuple[str, bool] - the name of the system and whether add/remove power (True/False)
        :param value: int - the amount of power to add/remove (default = 1)
        """

        system_name, action = action
        for installed_system_name in self.installed_systems.keys():
            if installed_system_name == system_name:
                room = self.installed_systems[installed_system_name]

                if action:
                    room.power += value
                else:
                    room.power -= value

                return
    
    def get_system_max_power(self, system: str) -> int:
        """
        Get the maximum power level of a system.
        :param system: str - the name of the system
        """

        for installed_system_name in self.installed_systems.keys():
            if installed_system_name == system:
                room = self.installed_systems[installed_system_name]
                return room.max_power
        
        print("Could not get the rooms max power: System not found!")
        return 0
    
    def check_if_system_accepts_power(self, system: str, value: int) -> bool:
        """
        Check's if the given system can accept the given power level.
        :param system: str - the name of the system
        :param value: int - the power level to check
        """

        for installed_system_name in self.installed_systems.keys():
            if installed_system_name == system:
                room = self.installed_systems[installed_system_name]
                return room.power + value <= room.max_power
        
        print("Could not check if system accepts power: System not found!")
        return False

    def activate_weapon(self, weapon: Weapon) -> bool:
        """
        Try to activate a weapon if there is enough power left. If successful, return True.
        :param weapon: Weapon - the weapon to activate
        """

        curr_power = self.current_power
        max_power = self.max_power 
        power_left = max_power - curr_power

        if power_left >= weapon.req_power and self.check_if_system_accepts_power("weapons", weapon.req_power):
            self.toggle_system_power(("weapons", True), weapon.req_power)
            weapon.activate()
            return True

        return False