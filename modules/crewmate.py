from __future__ import annotations
from typing import TYPE_CHECKING, Union
import pygame as pg

if TYPE_CHECKING:
    from modules.spaceship.spaceship import Spaceship
    from modules.spaceship.tile import Tile

from modules.resources import CrewmateRaces, copy_sprites, textures

class Crewmate(pg.sprite.Sprite):
    # public
    name: str
    rect: pg.Rect
    hitbox: pg.Rect
    race: CrewmateRaces
    moving_to: Union[Tile, None]
    movement_speed: int = 5

    selected: bool
    moving: bool
    boarding: bool

    # private
    _parent_ship : Spaceship
    _sprite_sheet: dict[str, pg.sprite.Sprite]
    _sprite: pg.sprite.Sprite
    _enemy: bool
    _occupied_tile: Union[Tile, None]
    _movement_queue: list[Tile]

    def __init__(self, 
                 name: str,
                 parent_ship: Spaceship,
                 pos: tuple[int, int],
                 offset = tuple[int, int],
                 sprite_group = pg.sprite.Group(),
                 race: CrewmateRaces = CrewmateRaces.HUMAN,
                 enemy: bool = False,
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)

        self._sprite_sheet = copy_sprites(textures["crewmates"][race.name]["base"])

        self._sprite = self._sprite_sheet["idle"]

        self.rect = self._sprite.rect
        self.rect.topleft = pos
        self.image = self._sprite.image.copy()

        self.hitbox = pg.Rect((pos[0] + offset[0], pos[1] + offset[1]), self._sprite.rect.size)
        
        self._parent_ship = parent_ship
        self._occupied_tile = None
        self.name = name
        self.race = race
        self.selected = False
        self.hovering = False
        self.moving = False
        self.moving_to = None
        self.boarding = False
        self._enemy = enemy
        self._movement_queue = []
    
    def update(self) -> None:
        if self.moving and self.moving_to is not None and len(self._movement_queue) > 0: # if the crewmate is moving, don't occupy any tiles
            if self.rect.center == self._movement_queue[0].rect.center:
                del self._movement_queue[0]
            else:
                x,y=0,0
                if self.rect.center[0] != self._movement_queue[0].rect.center[0]:
                    x = self.movement_speed if self.rect.center[0] < self._movement_queue[0].rect.center[0] else -self.movement_speed
                if self.rect.center[1] != self._movement_queue[0].rect.center[1]:
                    y = self.movement_speed if self.rect.center[1] < self._movement_queue[0].rect.center[1] else -self.movement_speed

                self.rect.move_ip(x,y)

            return 
        
        if self.boarding:
            # TODO: implement boarding logic
            return
        
        for room in self._parent_ship.rooms:
            colliding_tile = pg.sprite.spritecollideany(self, room)
            if colliding_tile is not None:
                self.occupied_tile = colliding_tile
                break
                
        return

    def draw(self, screen: pg.surface.Surface) -> None:
        # TODO: flip the sprite if enemy == True
        # TODO: if self.hovering == True, draw an outline around the crewmate
        # TODO: if self.selected == True, draw an outline around the crewmate

        screen.blit(self.image, self._sprite.rect)

    def check_hover(self, mouse_pos: tuple[int, int]) -> None:
        self.hovering = True if self.hitbox.collidepoint(mouse_pos) else False

    def check_clicked(self, mouse_pos: tuple[int,int], mouse_clicked: tuple[int, int, int]) -> None:
        if self.hitbox.collidepoint(mouse_pos) and mouse_clicked[0]:
            self.selected = True
        else:
            self.selected = False

    def move_to_tile(self, tile: Tile) -> None:
        self.moving = True
        self.selected = False
        self.moving_to = tile
        tile.selected = True

        self._movement_queue = self._parent_ship.get_path_between_tiles(self.occupied_tile, tile)
        del self.occupied_tile

    @property
    def occupied_tile(self) -> Union[Tile, None]:
        """Returns the tile the crewmate is currently occupying or None if moving."""
        return self._occupied_tile
    
    @occupied_tile.setter
    def occupied_tile(self, tile: Tile) -> None:
        """Sets the tile the crewmate is currently occupying."""
        self._occupied_tile = tile
        self._occupied_tile.occupied = True
    
    @occupied_tile.deleter
    def occupied_tile(self) -> None:
        """Removes the tile the crewmate is currently occupying."""
        self._occupied_tile.occupied = False
        self._occupied_tile = None