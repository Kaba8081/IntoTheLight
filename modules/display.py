import pygame as pg

from modules.spaceship.spaceship import Spaceship
from modules.player import Player
from modules.enemy import Enemy
from modules.ui import InterfaceController

class Display:
    def __init__(self, 
                 screen: pg.Surface, 
                 resolution: tuple[int, int],
                 ratio: float = 0.5, # player side / enemy side ratio
                 *args,
                 ) -> None:
        
        for arg in args:
            if isinstance(arg, Player):
                self.player = arg
            elif isinstance(arg, Enemy):
                self.enemy = arg

        if not hasattr(self, "player"):
            print("Player was not passed to display class!")

        self._interface = InterfaceController(resolution, args[0])
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

        player_center = self.player.get_center()
        new_player_center = (
            (self._screen.get_width() * self.ratio) / 2,
            (self._screen.get_height()) / 2
            )
        self.player.move_by_distance((
            new_player_center[0] - player_center[0],
            new_player_center[1] - player_center[1]
            ))
        self.player.place_doors()

        enemy_center = self.enemy.get_center()
        new_enemy_center = (
            (self._screen.get_height()) / 2,
            (self._screen.get_width() * (1-self.ratio)) / 2
            )
        self.enemy.move_by_distance((
            new_enemy_center[0] - enemy_center[0],
            new_enemy_center[1] - enemy_center[1],
            ))
        self.enemy.place_doors()

    def mouse_clicked(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[bool, bool, bool]) -> None:
        """
        Update the display based on the mouse position and click event.
        :param mouse_pos: tuple[int, int] - the current mouse position
        :param mouse_clicked: tuple[bool, bool, bool] - the current state of the mouse buttons
        """

        self._interface.mouse_clicked(mouse_pos, mouse_clicked)

        if hasattr(self, "enemy") and self.player.selected_weapon is not None:
            index = self.player.weapons.index(self.player.selected_weapon)

            room = self.enemy.select_room(mouse_pos, mouse_clicked, index)
            self.player.aimed_rooms[index] = room
            if room is not None: # a room was found at cursor position
                self.player.selected_weapon = None

    def check_mouse_hover(self, mouse_pos: tuple[int, int]) -> None:
        """
        Check if the mouse is hovering over any objects.
        :param mouse_pos: tuple[int, int] - the current mouse position
        """

        self._interface.check_mouse_hover(mouse_pos)
        
        if hasattr(self, "enemy") and self.player.selected_weapon is not None:
            self.enemy.hover_weapon(mouse_pos)

    def update(self) -> None:
        """
        Update the display.
        """

        self._interface.update()
        self._enemy_screen = pg.Surface((
            self._screen.get_height(),
            self._screen.get_width() * (1-self.ratio)
            ))
        self.enemy.draw(self._enemy_screen)
        self._enemy_screen = pg.transform.rotate(self._enemy_screen,90)

    def draw(self) -> None:
        """
        Draw's the display contents on screen.
        """

        self.player.draw(self._player_screen)

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