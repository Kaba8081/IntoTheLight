import pygame as pg

from modules.player import Player
from modules.spaceship.room import Room
from modules.spaceship.upgrades import Weapon
from modules.resources import textures, get_font

class InterfaceController(pg.sprite.Group):
    def __init__(self, resolution: tuple[int,int], player: Player) -> None:
        pg.sprite.Group.__init__(self)
        self.surface = pg.Surface(resolution, pg.SRCALPHA)
        self.resolution = resolution
        self._player = player

        # Power bar
        self._installed_systems_icon_bar = pg.sprite.Group()
        coords = [28, self.resolution[1]-32]
        for system_name in self._player.installed_systems:
            coords [0] += 36
            system = self._player.installed_systems[system_name]
            powered = True if system.power>0 else False

            power_icon = PowerIcon(powered, system_name, system, coords, self._installed_systems_icon_bar)
            self._installed_systems_icon_bar.add(power_icon)

        self._player_power_max = player.max_power
        self._player_power_current = self._player_power_max

        # Weapons bar

        self._wbar_module_size = 4
        self._wbar_gap = 2
        self._wbar_module_width = 126
        self._wbar_module_height = 64
    
        self._wbar_width = ((self._wbar_module_width + self._wbar_gap) * self._wbar_module_size) - self._wbar_gap + 2
        self._wbar_height = self._wbar_module_height + 48
        self._wbar_surface = pg.Surface((self._wbar_width+self._wbar_gap, self._wbar_height+self._wbar_gap), pg.SRCALPHA)

        coords[0] += 72
        coords[1] -= self._wbar_height
        self._wbar_coords = coords

        self._weapons = []
        self._weapon_icons = []
        for weapon in self._player.weapons:
            self.__weapons = self._weapons + [weapon]

        for index, weapon in enumerate(self.__weapons):
            self._weapon_icons.append(
                WeaponIcon(self._player, 
                           weapon,
                           (
                               (self._wbar_module_width + self._wbar_gap) * index+2,
                               48 + 2
                           ),
                           (
                               (self._wbar_module_width + self._wbar_gap) * index + self._wbar_coords[0],
                               48 + self._wbar_coords[1]
                           ),
                           (
                               self._wbar_module_width,
                               self._wbar_module_height - 2
                           )
                           )
            )

    def _draw_power(self) -> None:
        """Draws every element of the power bar"""
        
        color_on = (106, 190, 48)
        color_off = (132, 126, 135)

        curr_power = self._player_power_max - self._player_power_current

        # draw ship's power bar
        coords = (16, self.resolution[1]-32)
        for i in range(0, self._player_power_max):
            if i < curr_power: # draw full bar
                pg.draw.rect(self.surface, color_on, (coords[0], coords[1] - i * 20, 32, 16))
            else: # draw empty bar
                pg.draw.rect(self.surface, color_off, (coords[0], coords[1] - i * 20, 32, 16), 2)

        # draw every system's power bar
        for index, system_name in enumerate(self._player.installed_systems):
            system = self._player.installed_systems[system_name]
            system_power = system.power
            system_icon = "{system_name}_icon_{state}".format(state="on" if system_power > 0 else "off", system_name=system_name)
            
            coords = (64 + 36 * index, self.resolution[1]-32)
            self.surface.blit(textures[system_icon], coords)

            for power_level in range(0, system.max_power):
                if  power_level < system_power: # draw full bar
                    pg.draw.rect(self.surface, color_on, (coords[0] + 2, coords[1] - 24 - power_level*18, 28, 16))
                else: # draw empty bar
                    pg.draw.rect(self.surface, color_off, (coords[0] + 2, coords[1] - 24 - power_level*18, 28, 16), 2)
        return
    
    def _draw_weapons(self) -> None:
        """Draws the weapons interface on the screen"""
        
        self._wbar_surface.fill((0,0,0))
        for w_icon in self._weapon_icons:
            w_icon.draw(self._wbar_surface)

        pg.draw.lines(
            self._wbar_surface,
            (255,255,255),
            True,
            [
                # top left -> top right
                (0,48),
                (self._wbar_width, 48),
                # top right -> bottom right
                (self._wbar_width, 48),
                (self._wbar_width, self._wbar_height),
                # bottom right -> bottom left
                (self._wbar_width, self._wbar_height),
                (0, self._wbar_height),
                # bottom left -> top left
                (0, self._wbar_height),
                (0, 48)
            ],
            2
        )
        self.surface.blit(self._wbar_surface, self._wbar_coords)
    
    def mouse_clicked(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[int, int, int]) -> None:
        # handle user input
        for picon in self._installed_systems_icon_bar:
            if picon.rect.collidepoint(mouse_pos):
                picon.toggle(mouse_clicked)
                break

        for wicon in self._weapon_icons:
            if wicon.hitbox.collidepoint(mouse_pos):
                wicon.toggle(True, mouse_clicked)
            else:
                wicon.toggle(False)

    def check_mouse_hover(self, mouse_pos: tuple[int, int]) -> None:
        # check if the mouse is hovering over any of the weapon icons
        for wicon in self._weapon_icons:
            wicon.hovering = True if wicon.hitbox.collidepoint(mouse_pos) else False

    def update(self) -> None:
        self._player_power_current = self._player.current_power
        self.surface = pg.Surface(self.resolution, pg.SRCALPHA)

        # draw texture sprites
        for sprite in self.sprites():
            sprite.draw(self.surface)
        self._installed_systems_icon_bar.update()

        self._draw_power()
        self._installed_systems_icon_bar.draw(self.surface)

        for wicon in self._weapon_icons:
            wicon.update()

        self._draw_weapons()

    def draw(self, screen: pg.surface.Surface) -> None:
        screen.blit(self.surface, (0,0))

    @property
    def __weapons(self) -> list[Weapon]:
        return self._weapons
    
    @__weapons.setter
    def __weapons(self, weapon: Weapon) -> None:
        self._weapons = weapon

class PowerIcon(pg.sprite.Sprite):
    def __init__(self, 
                 powered: bool,
                 system_name: str, room_obj: Room, 
                 coords: tuple[int, int],
                 group: pg.sprite.Group) -> None:
        pg.sprite.Sprite.__init__(self, group)
        self._room_obj = room_obj
        self.powered = powered
        self.system_name = system_name
        self.coords = coords
        
        self.image = textures["{system}_icon_{state}".format(system=self.system_name, state="on" if powered else "off")]
        self.rect = self.image.get_rect(topleft=self.coords)

    def update(self) -> None:
        """Update the power icon based on the power level of the system."""
        power = self._room_obj.power
        self.image = textures["{system}_icon_{state}".format(system=self.system_name, state="on" if power > 0 else "off")]

    def draw(self, surface: pg.surface.Surface) -> None:
        """Draw the power icon to the provided pygame.surface.Surface"""
        surface.blit(self.image, self.rect)

    def toggle(self, mouse_clicked: tuple[int, int, int]) -> None:
        """Update the corresponding system power level based on user input."""
        if mouse_clicked[0]: # add power if possible
            self._room_obj.power += 1
        elif mouse_clicked[2]: # remove power if possible
            self._room_obj.power -= 1

        return
    
    def __str__(self) -> str:
        return self.system_name

class WeaponIcon():
    def __init__(self, player: Player, weapon: Weapon, pos: tuple[int, int], real_pos: tuple[int, int], size: tuple[int, int]) -> None:
        self._player = player
        self._weapon = weapon
        self._font = get_font("arial", 16)
        self._label = self._font.render(str(weapon), True, (255,255,255))
        
        self._colors = {
            "disabled": (135, 135, 135),
            "charging": (50,50,50),
            "ready": (135, 247, 104),
            "hovering": (100, 100, 100),
            "ready_hovering": (94, 186, 69),
            "selected": (247, 198, 74)
        }

        self.rect = pg.Rect(pos, size)
        self.hitbox = pg.Rect(real_pos, size)
        self.hovering = False
        self.selected = False
        self.state = "disabled"

    def update(self) -> None:
        self.state = self._weapon.state

    def draw(self, screen: pg.surface.Surface) -> None:
        color = self._colors[self.state]
        if self.hovering:
            color = self._colors["hovering"]
        if self.hovering and self.state == "ready":
            color = self._colors["ready_hovering"]
        if self.selected and self.state == "ready":
            color = self._colors["selected"]

        pg.draw.rect(screen, color, self.rect, 4) # draw outline         
        
        label_center = (self.rect.centerx - self._label.get_width()//2, self.rect.centery)
        screen.blit(self._label, label_center)

        return
    
    def toggle(self, clicked: bool, mouse_clicked: tuple[int, int, int] = (0,0,0)) -> None:
        if not clicked:
            self.selected = False 
        
        if mouse_clicked[0]:
            if self.state == "ready":
                self._player.selected_weapon = self._weapon
                self.selected = True
            else:
                self._weapon.start_charging()
                self.state = "charging"
        elif mouse_clicked[2]:
            self._player.selected_weapon = None
            self._weapon.disable()
            self.state = "disabled"