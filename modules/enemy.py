from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.upgrades import *

from modules.spaceship.spaceship import Spaceship
from modules.spaceship.room import Room

from random import randint

class Enemy(Spaceship):
    # public 
    hull_hp: int

    def __init__(self, 
                 ship_type: str = "cruiser",
                 screen_size: tuple[int, int] = (800, 600),
                 offset: tuple[int, int] = (0,0),
                 ) -> None:
        super().__init__(ship_type, screen_size, True, offset)

        self.hull_hp = randint(12,20)
    
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

    def activate_weapon(self, weapon: Weapon) -> bool:
        """
        Try to activate a weapon if there is enough power left. If successful, return True.
        :param weapon: Weapon - the weapon to activate
        """

        # TODO: implement enemy power management

        return True