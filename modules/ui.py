import pygame as pg

from modules.player import Player
from modules.spaceship.room import Room
from modules.resources import textures

class InterfaceController(pg.sprite.Group):
    def __init__(self, resolution: tuple[int,int], player: Player) -> None:
        pg.sprite.Group.__init__(self)
        self.surface = pg.Surface(resolution, pg.SRCALPHA)
        self.resolution = resolution
        self.player = player

        self._installed_systems_icon_bar = pg.sprite.Group()
        for index, system_name in enumerate(self.player.installed_systems):
            coords = (64 + 36 * index, self.resolution[1]-32)
            system = self.player.installed_systems[system_name]
            powered = True if system.power>0 else False

            power_icon = PowerIcon(powered, system_name, system, coords, self._installed_systems_icon_bar)
            self._installed_systems_icon_bar.add(power_icon)

        self._player_power_max = player.max_power
        self._player_power_current = self._player_power_max
    
    def _draw_power(self) -> None:
        """Draws every element of the power bar"""
        
        color_on = (106, 190, 48)
        color_off = (132, 126, 135)

        # draw ship's power bar
        coords = (16, self.resolution[1]-32)
        for i in range(0, self._player_power_max):
            if i < self._player_power_current: # draw full bar
                pg.draw.rect(self.surface, color_on, (coords[0], coords[1] - i * 20, 32, 16))
            else: # draw empty bar
                pg.draw.rect(self.surface, color_off, (coords[0], coords[1] - i * 20, 32, 16), 2)

        # draw every system's power bar
        for index, system_name in enumerate(self.player.installed_systems):
            system = self.player.installed_systems[system_name]
            system_power = system.power
            system_icon = "{system_name}_icon_{state}".format(state="on" if system_power > 0 else "off", system_name=system_name)
            
            coords = (64 + 36 * index, self.resolution[1]-32)
            self.surface.blit(textures[system_icon], coords)

            for power_level in range(0, system.max_power):
                if  power_level < system_power: # draw full bar
                    pg.draw.rect(self.surface, color_on, (coords[0] + 2, coords[1] - 24 - power_level*18, 28, 16))
                else: # draw empty bar
                    pg.draw.rect(self.surface, color_off, (coords[0] + 2, coords[1] - 24 - power_level*18, 28, 16), 2)

    def update(self) -> None:
        self._player_power_current = self.player.current_power
        self.surface = pg.Surface(self.resolution, pg.SRCALPHA)

        # draw texture sprites
        for sprite in self.sprites():
            sprite.draw(self.surface)

        self._draw_power()
        self._installed_systems_icon_bar.draw(self.surface)

    def draw(self, screen: pg.surface.Surface) -> None:
        screen.blit(self.surface, (0,0))

class PowerIcon(pg.sprite.Sprite):
    def __init__(self, 
                 powered: bool,
                 system_name: str, room_obj: Room, 
                 coords: tuple[int, int],
                 group: pg.sprite.Group) -> None:
        pg.sprite.Sprite.__init__(self, group)
        self.powered = powered
        self.system_name = system_name
        self.coords = coords
        
        self.image = textures["{system}_icon_{state}".format(system=self.system_name, state="on" if powered else "off")]
        self.rect = self.image.get_rect(topleft=self.coords)

    def update(self, power: int) -> None:
        """Update the power icon based on the power level of the system."""
        self.image = textures["{system}_icon_{state}".format(system=self.system_name, state="on" if power > 0 else "off")]

    def draw(self, surface: pg.surface.Surface) -> None:
        """Draw the power icon to the provided pygame.surface.Surface"""
        surface.blit(self.image, self.rect)