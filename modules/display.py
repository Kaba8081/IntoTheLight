import pygame as pg

from modules.spaceship import Spaceship
from modules.player import Player

class Display:
    def __init__(self, 
                 screen: pg.Surface, 
                 ratio: float = 0.5, # player side / enemy side ratio
                 *args,
                 ) -> None:
        self.screen = screen
        self.ratio = ratio

        for arg in args:
            if isinstance(arg, Player):
                self.player = arg
            elif isinstance(arg, Spaceship):
                self.enemy = arg
        
        if not hasattr(self, "player"):
            print("Player was not passed to display class!")

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

    def draw(self) -> None:
        self.player.draw(self.screen)