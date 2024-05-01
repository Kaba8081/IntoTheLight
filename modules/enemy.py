import pygame as pg
from typing import Union

from modules.spaceship.spaceship import Spaceship
from modules.spaceship.room import Room

class Enemy(Spaceship):
    def __init__(self, 
                 ship_type: str = "cruiser",
                 screen_size: tuple[int, int] = (800, 600),
                 offset: tuple[int, int] = (0,0),
                 ) -> None:
        super().__init__(ship_type, screen_size, True, offset)
    
    def select_room(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[bool, bool, bool]) -> Union[Room, None]:
        """
        Select a room if the cursor is hovering over it.
        :param mouse_pos: tuple[int, int] The current mouse position.
        :param mouse_clicked: tuple[bool, bool, bool] The current state of the mouse buttons.
        :return: Union[Room, None] The selected room or None if no room was found.
        """

        for room in self.rooms:
            if room.hitbox.collidepoint(mouse_pos):
                #room.aimed_at = False
                # TODO: Add an icon to show that the room is being targeted
                return room
        
        room.aimed_at = False
        return None


    def hover_weapon(self, mouse_pos: tuple[int, int]) -> None:
        """
        Highlight the room if the cursor is hovering over it.
        """

        for room in self.rooms:
            if room.hitbox.collidepoint(mouse_pos):
                room.aimed_at = True
            else:
                room.aimed_at = False
        
        return