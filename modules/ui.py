import pygame as pg

from modules.player import Player
from modules.resources import textures

class InterfaceController(pg.sprite.Group):
    def __init__(self, resolution: tuple[int,int], player: Player) -> None:
        pg.sprite.Group.__init__(self)
        self.surface = pg.Surface(resolution, pg.SRCALPHA)
        self.resolution = resolution
        self.player = player

        self._player_power_max = player.max_power
        self._player_power_current = self._player_power_max
    
    def _draw_power(self) -> None:
        coords = (16, self.resolution[1]-32)
        for i in range(0, self._player_power_max):
            if i < self._player_power_current:
                pg.draw.rect(self.surface, (106, 190, 48), (coords[0], coords[1] - i * 20, 32, 16))
            else:
                pg.draw.rect(self.surface, (132, 126, 135), (coords[0], coords[1] - i * 20, 32, 16), 2)

    def update(self) -> None:
        self._player_power_current = self.player.current_power

        self.surface = pg.Surface(self.resolution, pg.SRCALPHA)
        # draw texture sprites
        for sprite in self.sprites():
            sprite.draw(self.surface)

        # draw rect's
        self._draw_power()

    def draw(self, screen: pg.surface.Surface) -> None:
        screen.blit(self.surface, (0,0))