from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.enemy import Enemy
    from modules.spaceship.upgrades import Weapon
from modules.player import Player
from modules.spaceship.room import Room
from modules.resources import textures, get_font, button_palletes, systems

class InterfaceController(pg.sprite.Group):
    # public
    surface: pg.Surface
    resolution: tuple[int, int]
    ratio: float

    # private
    _player: Player
    _player_power_max: int
    _player_power_current: int

    _enemy: Enemy

    _power_color_on = (100, 255, 98)
    _power_color_off = (255, 255, 255)
    _power_bar_size = (32, 8)
    _power_bar_gap = 10
    _power_system_bar_size = (24, 8)
    _power_system_bar_gap = 10
    _power_system_bar_icon_size = (32, 32)
    _power_gap_between_systems = (_power_system_bar_icon_size[0] + 8, _power_system_bar_icon_size[1] + 8)

    _installed_systems_icon_bar: pg.sprite.Group
    _wbar_surface: pg.Surface
    _wbar_width: int
    _wbar_height: int
    _wbar_coords: tuple[int, int]
    _wbar_module_size: int
    _wbar_gap: int
    _wbar_module_width: int
    _wbar_module_height: int
    _autofire_button: Button
    _weapons: list[Weapon]
    _weapon_icons: list[WeaponIcon]

    _status_surface: pg.Surface
    _status_bar_size: tuple[int, int]
    _status_bar_coords: tuple[int, int]
    _status_bar_ratio: float
    _resource_icons: list[ResourceIcon]

    _enemy_hud_surface: pg.Surface
    _enemy_hud_font: pg.font.Font
    _enemy_hull_label: pg.surface.Surface
    _enemy_shields_label: pg.surface.Surface

    def __init__(self, resolution: tuple[int,int], player: Player, ratio: float = .65, enemy: Enemy = None) -> None:
        pg.sprite.Group.__init__(self)
        self.surface = pg.Surface(resolution, pg.SRCALPHA)
        self.resolution = resolution
        self.ratio = ratio
        self._player = player
        self._enemy = enemy

        # Power bar
        self._installed_systems_icon_bar = pg.sprite.Group()
        coords = [self._power_bar_size[0] + 32, self.resolution[1]-self._power_gap_between_systems[1]]
        for system_name in self._player.installed_systems:
            system = self._player.installed_systems[system_name]
            powered = True if system.power>0 else False

            power_icon = PowerIcon(powered, system_name, system, coords, self._power_system_bar_icon_size, self._installed_systems_icon_bar)
            self._installed_systems_icon_bar.add(power_icon)
            coords [0] += self._power_gap_between_systems[0]

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

        self._autofire_button = Button(
            self._player, 
            "AUTOFIRE", 
            (0, 0), 
            offset=(self._wbar_coords[0], self._wbar_coords[1]), 
            padding=(32, 14),
            border_width=2,
            color_palette="autoaim", 
            font_size=18,
            toggle_func=self._player.toggle_autofire)
        self._autofire_button.update_pos((self._wbar_width - self._autofire_button.rect.width + self._wbar_gap, 48 - self._autofire_button.rect.height))

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
        
        # player's status bar
        self._status_bar_ratio = ratio - 0.1
        self._status_bar_coords = (32, 32)
        self._status_bar_size = (self.resolution[0] * self._status_bar_ratio, 128)
        self._status_surface = pg.Surface(self._status_bar_size, pg.SRCALPHA)

        roles = ["fuel", "missiles", "drones"]
        self._resource_icons = []
        for i in range(3):
            self._resource_icons.append(
                ResourceIcon(
                    self._player,
                    (128 + 76 * i, 64),
                    (64, 32),
                    roles[i]
                    )
                )
        self._resource_icons.append(ResourceIcon(self._player, (384, 0), (128, 48), "scrap", 24, 42))

        # Enemy hud elements
        self._enemy_hud_surface = pg.Surface((self.resolution[0] - (1-ratio), 128), pg.SRCALPHA)
        self._enemy_hud_font = get_font("arial", 16)
        self._enemy_hull_label = self._enemy_hud_font.render("HULL", True, (255,255,255))
        self._enemy_shields_label = self._enemy_hud_font.render("SHIELDS", True, (255,255,255))

    def _draw_power(self) -> None:
        """Draws power bar interface on screen."""
        curr_power = self._player_power_max - self._player_power_current

        # draw ship's power bar
        coords = (16, self.resolution[1]-32)
        for i in range(0, self._player_power_max):
            if i < curr_power: # draw full bar
                pg.draw.rect(self.surface, self._power_color_on, (coords[0], coords[1] - i * self._power_bar_gap, self._power_bar_size[0], self._power_bar_size[1]))
            else: # draw empty bar
                pg.draw.rect(self.surface, self._power_color_off, (coords[0], coords[1] - i * self._power_bar_gap, self._power_bar_size[0], self._power_bar_size[1]), 1)

        # draw every system's power bar
        for index, system_name in enumerate(self._player.installed_systems):
            system = self._player.installed_systems[system_name]
            system_power = system.power
            
            coords = (self._power_bar_size[0] + 32 + (self._power_gap_between_systems[0] * index), self.resolution[1] - self._power_gap_between_systems[1])

            coords = (coords[0] + (self._power_system_bar_icon_size[0]//2 - self._power_system_bar_size[0]//2), coords[1] - (self._power_system_bar_icon_size[1]//2))
            for power_level in range(0, system.max_power):
                if  power_level < system_power: # draw full bar
                    pg.draw.rect(self.surface, self._power_color_on, (coords[0], coords[1] - power_level*self._power_system_bar_gap, self._power_system_bar_size[0], self._power_system_bar_size[1]))
                else: # draw empty bar
                    pg.draw.rect(self.surface, self._power_color_off, (coords[0], coords[1] - power_level*self._power_system_bar_gap, self._power_system_bar_size[0], self._power_system_bar_size[1]), 2)
        return
    
    def _draw_weapons(self) -> None:
        """Draws the weapons interface on the screen"""
        
        self._wbar_surface.fill((0,0,0))
        self._autofire_button.draw(self._wbar_surface)

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
    
    def _draw_status_bar(self) -> None:
        self._status_surface.fill((0,0,0))

        color_on = (106, 190, 48)

        # draw hull hp
        for i in range(self._player.hull_hp):
            pg.draw.rect(self._status_surface, color_on, (i*12, 16, 8, 16))
        
        # draw resources
        for icon in self._resource_icons:
            icon.draw(self._status_surface)

        self.surface.blit(self._status_surface, self._status_bar_coords)

        return

    def mouse_clicked(self, mouse_pos: tuple[int, int], mouse_clicked: tuple[int, int, int]) -> None:
        """
        Check if the mouse is clicking on any of the interface elements.
        :param mouse_pos: tuple[int, int] - the mouse's position
        :param mouse_clicked: tuple[int, int, int] - the state of the mouse buttons
        """

        for picon in self._installed_systems_icon_bar:
            if picon.hitbox.collidepoint(mouse_pos):
                picon.toggle(mouse_clicked)
                break

        for wicon in self._weapon_icons:
            if wicon.hitbox.collidepoint(mouse_pos):
                wicon.toggle(True, mouse_clicked)
            else:
                wicon.toggle(False)

        self._autofire_button.check_clicked(mouse_pos, mouse_clicked)

    def check_mouse_hover(self, mouse_pos: tuple[int, int]) -> None:
        """
        Check if the mouse is hovering over any of the interface elements.
        :param mouse_pos: tuple[int, int] - the mouse's position
        """

        for wicon in self._weapon_icons:
            wicon.hovering = True if wicon.hitbox.collidepoint(mouse_pos) else False

        self._autofire_button.check_hover(mouse_pos)

    def update(self) -> None:
        """
        Update the interface elements.
        """

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

        self._draw_status_bar()

    def draw(self, screen: pg.surface.Surface) -> None:
        """
        Draw the interface to the provided surface.
        :param screen: pg.surface.Surface - the surface to draw the interface on
        """
        
        screen.blit(self.surface, (0,0), special_flags=pg.BLEND_MAX)
        # BLEND_MAX make sure the ui is drawn on top of everything else, while still being transparent

    def draw_enemy_interface(self, screen: pg.surface.Surface) -> None:
        """
        Draw the enemy interface to the provided surface.
        :param screen: pg.surface.Surface - the surface to draw the enemy interface on
        """
        self._enemy_hud_surface = pg.Surface((self.resolution[0] * (1-self.ratio), 128), pg.SRCALPHA)
        if self._enemy is None:
            return

        coords = [32,32]
        self._enemy_hud_surface.blit(self._enemy_hull_label, coords)
        coords[1] += self._enemy_hull_label.get_height() + 16
        for i in range(self._enemy.hull_hp):
            pg.draw.rect(self._enemy_hud_surface, self._power_color_on, (coords[0] + i*12, coords[1], 8, 16))
        coords[1] += 32
        self._enemy_hud_surface.blit(self._enemy_shields_label, coords)

        # TODO: draw shields icons for enemy shields

        screen.blit(self._enemy_hud_surface, (0,0))

        return

    def dev_draw_ui_areas(self, screen: pg.Surface) -> None:
        self._wbar_surface.fill((255,0,0))
        self.surface.blit(self._wbar_surface, self._wbar_coords)
        self._status_surface.fill((255,0,0))
        self.surface.blit(self._status_surface, self._status_bar_coords)
        self._enemy_hud_surface.fill((255,0,0))
        screen.blit(self._enemy_shields_label, (self.resolution[0] * self.ratio, 0))
        screen.blit(self.surface, (0,0))

    @property
    def __weapons(self) -> list[Weapon]:
        return self._weapons
    
    @__weapons.setter
    def __weapons(self, weapon: Weapon) -> None:
        self._weapons = weapon

class PowerIcon(pg.sprite.Sprite):
    # public
    powered: bool
    system_name: str
    coords: tuple[int, int]
    image: pg.surface.Surface
    rect: pg.Rect

    # private
    _room_obj: Room

    def __init__(self, 
                 powered: bool,
                 system_name: str, room_obj: Room, 
                 coords: tuple[int, int],
                 size: tuple[int, int],
                 group: pg.sprite.Group) -> None:
        pg.sprite.Sprite.__init__(self, group)
        self._room_obj = room_obj
        self.system_name = system_name
        self.coords = coords
        # textures["system_icons"][system_name]["green" if powered else "grey"]
        self.icon = textures["system_icons"][system_name]["green" if powered else "grey"]
        self.image = self.icon.image
        self.rect = self.image.get_rect(center=(coords[0] + size[0]//2, coords[1] + size[1]//2))
        self.hitbox = pg.Rect(coords, size)

    def update(self) -> None:
        """Update the power icon based on the power level of the system."""
        power = self._room_obj.power
        self.icon = textures["system_icons"][self.system_name]["green" if power>0 else "grey"]
        self.image = self.icon.image.convert_alpha()

    def toggle(self, mouse_clicked: tuple[int, int, int]) -> None:
        """Update the corresponding system power level based on user input."""
        if self.system_name in ["weapons"]: # weapons are handled separately
            return

        if mouse_clicked[0]: # add power if possible
            self._room_obj.power += 1
        elif mouse_clicked[2]: # remove power if possible
            self._room_obj.power -= 1

        return
    
    def __str__(self) -> str:
        return self.system_name

class WeaponIcon():
    # public
    rect: pg.Rect
    hitbox: pg.Rect
    hovering: bool
    selected: bool
    state: str

    # private
    _colors = {
        "disabled": (135, 135, 135),
        "charging": (230,230,230),
        "ready": (135, 247, 104),
        "hovering": (100, 100, 100),
        "ready_hovering": (94, 186, 69),
        "selected": (247, 198, 74)
    }
    _player: Player
    _weapon: Weapon
    _font: pg.font.Font
    _label: pg.surface.Surface

    def __init__(self, player: Player, weapon: Weapon, pos: tuple[int, int], real_pos: tuple[int, int], size: tuple[int, int]) -> None:
        self._player = player
        self._weapon = weapon
        self._font = get_font("arial", 16)
        self._label = self._font.render(str(weapon), True, (255,255,255))

        self.rect = pg.Rect(pos, size)
        self.hitbox = pg.Rect(real_pos, size)
        self.hovering = False
        self.selected = False
        self.state = "disabled"

    def update(self) -> None:
        """
        Update the icon state if there were any changes.
        """
        self.state = self._weapon.state

        self.selected = True if self._player.selected_weapon == self._weapon else False

    def draw(self, screen: pg.surface.Surface) -> None:
        color = self._colors[self.state]
        if self.hovering:
            color = self._colors["hovering"]
        if self.hovering and self.state == "ready":
            color = self._colors["ready_hovering"]
        if self.selected and (self.state == "ready" or self.state == "charging"):
            color = self._colors["selected"]

        pg.draw.rect(screen, color, self.rect, 4) # draw outline         
        
        label_center = (self.rect.centerx - self._label.get_width()//2, self.rect.centery)
        screen.blit(self._label, label_center)

        return
    
    def toggle(self, clicked: bool, mouse_clicked: tuple[int, int, int] = (0,0,0)) -> None:
        """
        Update the weapon's state based on user input.
        :param clicked: bool - whether the object was clicked (mouse over it)
        :param mouse_clicked: tuple[int, int, int] - the state of the mouse buttons
        """
        if not clicked:
            self.selected = False 
        
        if mouse_clicked[0]:
            if self.state == "ready" or self.state == "charging":
                self._player.selected_weapon = self._weapon
                self.selected = True
                if self._weapon.target is not None:
                    self._weapon.target = None
            elif self._weapon.state == "disabled": # try to activate the weapon
                if self._player.activate_weapon(self._weapon):
                    self.state = "charging"
                else:
                    self.not_enough_power()
        elif mouse_clicked[2] and self.state in ["charging", "ready", "selected"]:
            self._player.selected_weapon = None
            self._player.toggle_system_power(("weapons", False), self._weapon.req_power)
            if self._weapon.target is not None:
                self._weapon.target = None
            self._weapon.disable()
            self.state = "disabled"
    
    def not_enough_power(self) -> None:
        """Displays a message that the weapon does not have enough power to be activated."""
        
        # TODO: implement this

        return

class ResourceIcon():
    # public
    role: str
    pos: tuple[int, int]
    rect: pg.Rect

    # private
    _color_normal = (255, 255, 255)
    _color_low = (190, 75, 75)
    _player: Player
    _icon: pg.surface.Surface
    _icon_rect: pg.Rect
    _font: pg.font.Font

    def __init__(self, 
                 player: Player, 
                 pos: tuple[int, int], 
                 size: tuple[int, int], 
                 role: Literal["fuel", "missiles", "drone_parts", "scrap"],
                 font_size: int = 16,
                 icon_size: int = 24
                 ) -> None:
        """
        :param player: Player - the player object
        :param pos: tuple[int, int] - the position of the icon
        :param size: tuple[int, int] - the size of the icon
        :param role: str - the role of the resource icon
        :param font_size: int - the font size of the resource count
        """
        self._player = player
        self._icon = textures["ui_icons"][f"{role}"]
        self._icon_rect = self._icon.rect
        self._font = get_font("arial", font_size)

        self.role = role
        self.pos = pos
        self.rect = pg.Rect(pos, size)
        return 
    
    def draw(self, screen: pg.surface.Surface) -> None:
        """
        Draw the resource icon on the given surface.
        :param screen: pg.surface.Surface - the surface to draw on
        """
        resource_count = 0

        match self.role:
            case "fuel":
                resource_count = self._player.fuel
            case "missile":
                resource_count = self._player.missles
            case "drone_parts":
                resource_count = self._player.drones
            case "scrap":
                resource_count = self._player.scrap
        
        curr_color = self._color_normal if resource_count > 8 else self._color_low
        # draw the outline box
        pg.draw.rect(screen, curr_color, self.rect, 4)

        # draw the icon
        screen.blit(self._icon.image, (self.rect.centerx - self._icon_rect.width, self.rect.centery - self._icon_rect.height // 2))

        # draw the resource count
        label = self._font.render(str(resource_count), True, curr_color)
        label_center = (self.rect.centerx, self.rect.centery - label.get_height() // 2)
        
        screen.blit(label, label_center)

        return
    
class Button():
    def __init__(self,
                 player: Player,
                 label: str,
                 pos: tuple[int, int],
                 offset: tuple[int, int] = (0,0),
                 padding: Union[int, tuple[int,int]] = 32,
                 border_width: int = 0,
                 border_radius: int = 5,
                 color_palette: str = "default",
                 font_size: int = 16,
                 font: str = "arial",
                 toggle_func: callable = None
                 ) -> None:
        """
        :param player: Player - the player object
        :param label: str - the text displayed on the button
        :param pos: tuple[int, int] - the position of the button
        :param offset: tuple[int, int] - the offset of the label from the button's position
        :param padding: int - the padding around the label
        :param border_width: int - the width of the border (0 = no border)
        :param color_palette: str - the color palette of the button
        :param font_size: int - the font size of the label
        :param font: str - the font of the label
        """

        self._player = player
        self._color_palette = button_palletes[color_palette]
        self._font = get_font(font, font_size)
        self._border_width = border_width
        self._border_radius = border_radius


        self.pos = pos
        self.text = label
        self.state = "normal"
        self.hovering = False

        if toggle_func is not None:
            self.toggle = toggle_func

        temp_label = self._font.render(self.text, True, self._color_palette["label"][self.state])
        temp_label_size = temp_label.get_size()
        size = (temp_label_size[0] + padding[0] + border_width, temp_label_size[1] + padding[1] + border_width)
        
        self.rect = pg.Rect(pos, size)
        self.hitbox = pg.Rect((pos[0] + offset[0], pos[1] + offset[1]), size)

        return
    
    def update_pos(self, offset: tuple[int, int]) -> None:
        self.rect.x += offset[0]
        self.rect.y += offset[1]
        self.hitbox.x += offset[0]
        self.hitbox.y += offset[1]

    def draw(self, screen: pg.surface.Surface) -> None:
        state = f"{self.state}_hover" if self.hovering else self.state
        pg.draw.rect(screen, self._color_palette["background"][state], self.rect, 0, self._border_radius)
        pg.draw.rect(screen, self._color_palette["border"][state], self.rect, self._border_width, self._border_radius)

        label = self._font.render(self.text, True, self._color_palette["label"][state])
        label_center = (self.rect.centerx - label.get_width() // 2, self.rect.centery - label.get_height() // 2)

        screen.blit(label, label_center)

        return
    
    def check_hover(self, mouse_pos: tuple[int, int]) -> None:
        self.hovering = True if self.hitbox.collidepoint(mouse_pos) else False
    
    def check_clicked(self, mouse_pos: tuple[int,int], mouse_clicked: tuple[int, int, int]) -> None:
        if self.hitbox.collidepoint(mouse_pos) and mouse_clicked[0]:
            if hasattr(self, "toggle"):
                self.state = "clicked" if self.toggle() else "normal"