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
        self.screen = screen
        self.ratio = ratio

        self.player_screen = pg.Surface((
            screen.get_width() * self.ratio,
            screen.get_height()
            ))
        self.enemy_screen = pg.Surface((
            screen.get_width() - (screen.get_width() * self.ratio),
            screen.get_height()
            ))

        player_center = self.player.get_center()
        new_player_center = (
            (self.screen.get_width() * self.ratio) / 2,
            (self.screen.get_height()) / 2
            )
        self.player.move_by_distance((
            new_player_center[0] - player_center[0],
            new_player_center[1] - player_center[1]
            ))
        self.player.find_bordering_rooms()

        enemy_center = self.enemy.get_center()
        new_enemy_center = (
            (self.screen.get_width() * self.ratio) / 2,
            (self.screen.get_height()) / 2
            )
        self.enemy.move_by_distance((
            new_enemy_center[0] - enemy_center[0],
            new_enemy_center[1] - enemy_center[1]
            ))
        self.enemy.find_bordering_rooms()

    def update(self) -> None:
        self._interface.update()

    def draw(self) -> None:
        self.player.draw(self.player_screen)
        self.enemy.draw(self.enemy_screen)

        self.screen.blit(self.player_screen, (0,0))
        
        self.enemy_screen = pg.transform.flip(self.enemy_screen, True, False)
        self.screen.blit(self.enemy_screen, (self.screen.get_width() * self.ratio, 0))

        pg.draw.line(self.screen, (255,255,255), 
                (self.screen.get_width() * self.ratio, 0), 
                (self.screen.get_width() * self.ratio, self.screen.get_height()), 
                2)
        
        self._interface.draw(self.screen)
        self.player_screen.fill((0,0,0))
        self.enemy_screen.fill((0,0,0))