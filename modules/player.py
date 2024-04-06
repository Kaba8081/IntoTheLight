import pygame as pg
from typing import Union

from modules.spaceship.spaceship import *

class Player(Spaceship):
    def __init__(self, 
                 ship_type: str = "scout"
                 ) -> None:
        Spaceship.__init__(self, ship_type)
    
    def update(self, dt: float, mouse_pos: tuple[int, int], mouse_clicked: list = None) -> None:
        for door in self.doors:
            if door.rect.collidepoint(mouse_pos):
                door.hovering = True
                if mouse_clicked is not None and mouse_clicked[0]:
                    door.open()

    @property
    def empty_upgrade_slots(self) -> Union[list, None]:
        empty_slots = []
        for room in self.rooms:
            room_slots = room.upgrade_slots
            if room_slots is not None:
                empty_slots.append(room_slots)
            
        return empty_slots if len(empty_slots) > 0 else None

    @property
    def weapons(self) -> Union[list, None]:
        weapons = []
        for room in self.rooms:
            room_weapons = room.weapons
            if room_weapons is not None:
                weapons.append(room_weapons)
            
        return weapons if len(weapons) > 0 else None
    
    @property
    def thrusters(self) -> Union[list, None]:
        thrusters = []
        for room in self.rooms:
            room_thrusters = room.thrusters
            if room_thrusters is not None:
                thrusters.append(room_thrusters)
            
        return thrusters if len(thrusters) > 0 else None
