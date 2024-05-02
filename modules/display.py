from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.spaceship import Spaceship
from modules.player import Player
from modules.enemy import Enemy

from modules.ui import InterfaceController

class Display:
    def __init__(self, 
                 screen: pg.Surface, 
                 resolution: tuple[int, int],
                 ratio: float = 0.65, # player side / enemy side ratio
                 *args,
                 ) -> None:
        
        for arg in args:
            if type(arg) is Player:
                self._player = arg
            elif type(arg) is Enemy:
                self.enemy_ship = arg

        if not hasattr(self, "player"):
            print("Player was not passed to display class!")

        self._interface = InterfaceController(resolution, self._player, ratio=ratio, enemy=self.enemy_ship)
        self._screen = screen
        self.ratio = ratio

        self._player_screen = pg.Surface((
            screen.get_width() * self.ratio,
            screen.get_height()
            ))
        self._enemy_screen = pg.Surface((
            self._screen.get_height(),
            self._screen.get_width() * (1-self.ratio)
            ))
        
        self.place_ship(self._player, ratio=self.ratio)
        self.place_ship(self.enemy_ship, ratio=self.ratio, enemy=True)

    def mouse_clicked(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[bool, bool, bool]) -> None:
        """
        Update the display based on the mouse position and click event.
        :param mouse_pos: tuple[int, int] - the current mouse position
        :param mouse_clicked: tuple[bool, bool, bool] - the current state of the mouse buttons
        """

        self._interface.mouse_clicked(mouse_pos, mouse_clicked)

        if self.enemy_ship is not None and self._player.selected_weapon is not None:
            room = self.enemy_ship.select_room(mouse_pos, mouse_clicked)
            self._player.selected_weapon.target = room

            if room is not None: # a room was found at cursor position
                room.targeted = True
                self._player.selected_weapon = None

    def check_mouse_hover(self, mouse_pos: tuple[int, int]) -> None:
        """
        Check if the mouse is hovering over any objects.
        :param mouse_pos: tuple[int, int] - the current mouse position
        """

        self._interface.check_mouse_hover(mouse_pos)
        
        if self.enemy_ship is not None and self._player.selected_weapon is not None:
            self.enemy_ship.hover_weapon(mouse_pos)

    def update(self) -> None:
        """
        Update the display.
        """
        self._enemy_screen = pg.Surface((
            self._screen.get_height(),
            self._screen.get_width() * (1-self.ratio)
            ))
        
        self._player.draw(self._player_screen)
        self.enemy_ship.draw(self._enemy_screen)

        self._player.draw_projectiles(self._player_screen, self._enemy_screen)
        self.enemy_ship.draw_projectiles(self._enemy_screen, self._player_screen)

        self._interface.update()
        self._enemy_screen = pg.transform.rotate(self._enemy_screen,90)

    def draw(self) -> None:
        """
        Draw's the display contents on screen.
        """

        self._screen.blit(self._player_screen, (0,0))
        self._screen.blit(self._enemy_screen, (self._screen.get_width() * self.ratio, 0))

        # debug - draw border line between player / enemy cameras
        pg.draw.line(self._screen, (255,255,255), 
                (self._screen.get_width() * self.ratio, 0), 
                (self._screen.get_width() * self.ratio, self._screen.get_height()), 
                2)
        
        self._interface.draw(self._screen)
        self._player_screen.fill((0,0,0))
        self._enemy_screen.fill((0,0,0))

    def place_ship(self, ship: Spaceship, ratio: float = 0.65, enemy: bool = False) -> None:
        ship_center = ship.get_center()
        new_center = (0,0)
        if enemy:
            new_center = (
            (self._screen.get_height()) / 2,
            (self._screen.get_width() * (1-self.ratio)) / 2
            )
        else:
            new_center = (
            (self._screen.get_width() * self.ratio) / 2,
            (self._screen.get_height()) / 2
            )
        ship.move_by_distance((
            new_center[0] - ship_center[0],
            new_center[1] - ship_center[1]
            ))
        ship.place_doors()

    @property
    def enemy_ship(self) -> Union[Enemy, None]:
        return self._enemy
    
    @enemy_ship.setter
    def enemy_ship(self, value: Union[Enemy, None]) -> None: #TODO: change User Interface if enemy is changed
        if value == None:
            pass
        else:
            self._enemy = value