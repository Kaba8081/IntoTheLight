import pygame as pg
from modules.resources import CrewmateRaces, copy_sprites, textures

class Crewmate(pg.sprite.Sprite):
    # public
    name: str
    hitbox: pg.Rect
    race: CrewmateRaces

    moving: bool

    # private
    _sprite_sheet: dict[str, pg.sprite.Sprite]
    _sprite: pg.sprite.Sprite
    _enemy: bool

    def __init__(self, 
                 name: str,
                 pos: tuple[int, int],
                 offset = tuple[int, int],
                 sprite_group = pg.sprite.Group(),
                 race: CrewmateRaces = CrewmateRaces.HUMAN,
                 enemy: bool = False,
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)

        self.name = name
        self.race = race
        self._sprite_sheet = copy_sprites(textures["crewmates"][race.name]["base"])

        self._sprite = self._sprite_sheet["idle"]

        self.rect = self._sprite.rect
        self.rect.topleft = pos
        self.image = self._sprite.image

        self.hitbox = pg.Rect((pos[0] + offset[0], pos[1] + offset[1]), self._sprite.rect.size)

        self.selected = False
        self._enemy = enemy
    
    def update(self) -> None:
        # TODO: find the tile which the crewmate is on and occupy it

        pass

    def draw(self, screen: pg.surface.Surface) -> None:
        # TODO: flip the sprite if enemy == True

        screen.blit(self._sprite.image, self._sprite.rect)
    
    def move_by_distance(self, distance: tuple[int, int]) -> None:
        self.rect.x += distance[0]
        self.rect.y += distance[1]
