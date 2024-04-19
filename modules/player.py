import pygame as pg
from typing import Union

from modules.spaceship.spaceship import *
from modules.resources import ship_layouts, systems

class Player(Spaceship):
    def __init__(self, 
                 ship_type: str = "scout"
                 ) -> None:
        
        self.installed_systems = {}

        # required systems
        self._room_enine = None
        self._room_weapons = None
        self._room_oxygen = None
        self._room_bridge = None

        # required data about these systems
        self.installed_weapons = {}
        self.installed_thrusters = {}
        
        self.hull_hp = 100
        self.fuel = 16
        self.missles = 8
        self.drone_parts = 2
        self.currency = 10

        self.rooms = []
        self.doors = pg.sprite.Group()

        for room in ship_layouts[ship_type]["rooms"]:
            created_room = Room(
                room["pos"], 
                room["tiles"],
                role=room["role"] if "role" in room else None,
                level=room["level"] if "level" in room else 0,
                upgrade_slots=room["upgrade_slots"] if "upgrade_slots" in room else {},
                )
            self.rooms.append(created_room)

            if "role" in room and room["role"] in systems:
                self.installed_systems[room["role"]] = created_room
        
        # find and power essential systems
        for system_name in systems:
            match system_name:
                case "engines":
                    self._room_enine = self.installed_systems[system_name]
                    self._room_enine.power = 1
                case "weapons":
                    self._room_weapons = self.installed_systems[system_name]
                case "medbay":
                    self._room_medbay = self.installed_systems[system_name]
                case "o2":
                    self._room_oxygen = self.installed_systems[system_name]
                    self._room_oxygen.power = 1
                case "bridge":
                    self._room_bridge = self.installed_systems[system_name]
                    self._room_bridge.power = 1
    
    def update(self, dt: float, mouse_pos: tuple[int, int], mouse_clicked: list = None) -> None:
        for door in self.doors:
            if door.rect.collidepoint(mouse_pos):
                door.hovering = True
                if mouse_clicked is not None and mouse_clicked[0]:
                    door.open()
        
        for weapon in self.weapons:
            weapon.update()

    @property
    def empty_upgrade_slots(self) -> Union[list[UpgradeSlot], None]:
        empty_slots = []
        for room in self.rooms:
            room_slots = room.upgrade_slots
            if room_slots is not None:
                empty_slots.append(room_slots)
            
        return empty_slots if len(empty_slots) > 0 else None

    @property
    def weapons(self) -> list[Weapon]:
        weapons = []
        for room in self.rooms:
            room_weapons = room.weapons
            if room_weapons is not None:
                weapons = weapons + room_weapons
            
        return weapons
    
    @property
    def thrusters(self) -> Union[list[Thruster], None]:
        thrusters = []
        for room in self.rooms:
            room_thrusters = room.thrusters
            if room_thrusters is not None:
                thrusters.append(room_thrusters)
            
        return thrusters if len(thrusters) > 0 else None

    @property
    def max_power(self) -> int:
        """Return the maximum power that the ship generates."""

        return 6 + self._room_enine.level * 2 # base generation 6 + each level of the engine provides 2 power

    @property
    def current_power(self) -> int:
        """Return the current power usage of the ship."""

        power_level = 0
        for system in self.installed_systems:
            power_level += self.installed_systems[system].power
        return power_level

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
        """Get the maximum power level of a system.
        :param system: str - the name of the system
        """

        for installed_system_name in self.installed_systems.keys():
            if installed_system_name == system:
                room = self.installed_systems[installed_system_name]
                return room.max_power
        
        print("Could not get the rooms max power: System not found!")
        return 0
    
    def check_if_system_accepts_power(self, system: str, value: int) -> bool:
        """Check's if the given system can accept the given power level.
        :param system: str - the name of the system
        :param value: int - the power level to check
        """

        for installed_system_name in self.installed_systems.keys():
            if installed_system_name == system:
                room = self.installed_systems[installed_system_name]
                return room.power + value <= room.max_power
        
        print("Could not check if system accepts power: System not found!")
        return False