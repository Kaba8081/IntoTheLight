from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.spaceship import Spaceship
from modules.player import Player
from modules.enemy import Enemy

from modules.ui import InterfaceController

class Display:
    # public
    ratio: float

    # private
    _interface: InterfaceController
    _screen: pg.Surface
    _player_screen: pg.Surface
    
    _enemy: Union[Enemy, None]
    _enemy_screen: pg.Surface

    _player: Player
    _enemy: Union[Enemy, None]

    def __init__(self, 
                 screen: pg.Surface, 
                 resolution: tuple[int, int],
                 ratio: float = 0.65, # player side / enemy side ratio
                 player: Player = None,
                 enemy: Enemy = None,
                 ) -> None:

        self._interface = InterfaceController(resolution, player, ratio=ratio, enemy=enemy)
        self._screen = screen
        self.ratio = ratio

        self._player = player
        self._player_screen = pg.Surface((
            screen.get_width() * self.ratio,
            screen.get_height()
            ))
        
        self._enemy =None
        self._enemy_screen = None
        
        self.place_ship(self._player)
        self._player.move_hitbox_by_distance((((self._screen.get_width() - self._player_screen.get_width()) // 2), 0))

    def mouse_clicked(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[bool, bool, bool]) -> None:
        """
        Update the display based on the mouse position and click event.
        :param mouse_pos: tuple[int, int] - the current mouse position
        :param mouse_clicked: tuple[bool, bool, bool] - the current state of the mouse buttons
        """

        self._interface.mouse_clicked(mouse_pos, mouse_clicked)

        active_crewmate = None
        for crewmate in self._player.crewmates:
            # check for active crewmates before checking for room clicks
            if crewmate.selected == True:
                active_crewmate = crewmate

            crewmate.check_clicked(mouse_pos, mouse_clicked)
        
        if active_crewmate is not None:
            for room in self._player.rooms:
                tile = room.check_clicked(mouse_pos, mouse_clicked)

                if tile is not None:
                    if active_crewmate.moving == True and active_crewmate.moving_to is not None:
                        # if the crewmate was already moving to another tile, delesect it
                        active_crewmate.moving_to.selected = False
                    
                    active_crewmate.move_to_tile(tile)

                    break
        
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

        for crewmate in self._player.crewmates:
            # check for active crewmates before checking for room clicks
            if crewmate.selected == True:
                any_active_crewmates = True

            crewmate.check_hover(mouse_pos)

        if self.enemy_ship is not None and self._player.selected_weapon is not None:
            self.enemy_ship.hover_weapon(mouse_pos)

    def update(self) -> None:
        """
        Update the display.
        """
        
        self._player.draw(self._player_screen)

        if self.enemy_ship is not None and self._interface.enemy_ui_active:
            self._enemy_screen = pg.Surface((
                self._screen.get_height(),
                self._screen.get_width() * (1-self.ratio)
                ))
            self.enemy_ship.draw(self._enemy_screen)
            self._player.draw_projectiles(self._player_screen, self._enemy_screen)
            self.enemy_ship.draw_projectiles(self._enemy_screen, self._player_screen)
            self._enemy_screen = pg.transform.rotate(self._enemy_screen,90)
            
        self._interface.update()

    def draw(self) -> None:
        """
        Draw's the display contents on screen.
        """
        # TODO: Draw screen based if enemy ship is present or not

        if self.enemy_ship is not None and self._interface.enemy_ui_active:
            self._interface.draw_enemy_interface(self._enemy_screen)
            self._screen.blit(self._enemy_screen, (self._screen.get_width() * self.ratio, 0))

            # debug - draw border line between player / enemy cameras
            pg.draw.line(self._screen, (255,255,255), 
                    (self._screen.get_width() * self.ratio, 0), 
                    (self._screen.get_width() * self.ratio, self._screen.get_height()), 
                    2)
            self._screen.blit(self._player_screen, (0,0))
        else:
            player_pos = ((self._screen.get_width() - self._player_screen.get_width()) // 2, 0)
            self._screen.blit(self._player_screen, player_pos)     
        self._interface.draw(self._screen)

        self._player_screen.fill((0,0,0))
        if self.enemy_ship is not None and self._interface.enemy_ui_active:
            self._enemy_screen.fill((0,0,0))

        if self.enemy_ship is not None and self._interface.enemy_ui_active:
            self._enemy.dev_draw_room_hitboxes(self._screen)

    def place_ship(self, ship: Spaceship, enemy: bool = False, ratio: float = -1) -> None:
        # ratio arg was not parsed
        if ratio == -1:
            ratio = self.ratio
            
        ship_center = ship.get_center()
        new_center = (0,0)

        if enemy:
            new_center = (
            (self._screen.get_height()) / 2,
            (self._screen.get_width() * (1-ratio)) / 2
            )
        else:
            new_center = (
            (self._screen.get_width() * ratio) / 2,
            (self._screen.get_height()) / 2
            )

        ship.move_by_distance((
            new_center[0] - ship_center[0],
            new_center[1] - ship_center[1]
            ))
        ship.place_doors()
        if ship.installed_shield is not None:
            ship.installed_shield.post_init_update(ship.get_corners(), ship.get_center())

    def dev_draw_player_hitboxes(self) -> None:
        """
        Draw the player's hitboxes on screen.
        """
        for room in self._player.rooms:
            pg.draw.rect(self._screen, (255,0,0), room.hitbox, 1)
            for tile in room.sprites():
                pg.draw.rect(self._screen, (0,0,255), tile.hitbox, 1) if hasattr(tile, "hitbox") else None
        
        for crewmate in self._player.crewmates:
            pg.draw.rect(self._screen, (0,255,0), crewmate.hitbox, 1)

    @property
    def enemy_ship(self) -> Union[Enemy, None]:
        return self._enemy
    
    @enemy_ship.setter
    def enemy_ship(self, value: Enemy) -> None:
        self._enemy = value
        self._interface.enemy_ship = value

        self._enemy_screen = pg.Surface((
            self._screen.get_height(),
            self._screen.get_width() * (1-self.ratio)
            ))

        self.place_ship(self._enemy, True)
        self._player.move_hitbox_by_distance((-((self._screen.get_width() - self._player_screen.get_width()) // 2), 0))

    @enemy_ship.deleter
    def enemy_ship(self) -> None:
        self._enemy = None
        self._player.move_hitbox_by_distance((((self._screen.get_width() - self._player_screen.get_width()) // 2), 0))
        del self._interface.enemy_ship