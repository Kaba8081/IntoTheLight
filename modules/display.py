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
        self.player.find_bordering_rooms()

        enemy_center = self.enemy.get_center()
        new_enemy_center = (
            (self._screen.get_height()) / 2,
            (self._screen.get_width() * (1-self.ratio)) / 2
            )
        self.enemy.move_by_distance((
            new_enemy_center[0] - enemy_center[0],
            new_enemy_center[1] - enemy_center[1],
            ))
        self.enemy.find_bordering_rooms()

    def update_mouse(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[int,int,int]) -> None:
        self._interface.update_mouse(mouse_pos, mouse_clicked)
    def check_mouse_hover(self, mouse_pos: tuple[int, int]) -> None:
        self._interface.check_mouse_hover(mouse_pos)

    def update(self) -> None:
        self._interface.update()
        self._enemy_screen = pg.Surface((
            self._screen.get_height(),
            self._screen.get_width() * (1-self.ratio)
            ))
        self.enemy.draw(self._enemy_screen)
        self._enemy_screen = pg.transform.rotate(self._enemy_screen,90)

    def draw(self) -> None:
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