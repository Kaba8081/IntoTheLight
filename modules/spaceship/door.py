import pygame as pg

from modules.resources import textures

class Door(pg.sprite.Sprite):
    # public
    opened: bool
    rect: pg.Rect
    image: pg.Surface

    # private
    _txt_set: dict[str, pg.Surface]
    _txt_open: pg.Surface
    _txt_closed: pg.Surface

    def __init__(self, 
                 pos: tuple, 
                 sprite_group: pg.sprite.Group,
                 vertical: bool = False
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)

        self._txt_set = textures["door"]
        self._txt_closed = pg.transform.rotate(self._txt_set["closed"],90) if vertical else self._txt_set["closed"]
        self._txt_open = pg.transform.rotate(self._txt_set["open"],90) if vertical else self._txt_set["open"]
        self.image = self._txt_closed
        self.rect = self.image.get_rect()

        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

        self.opened = False

    def toggle(self) -> None:
        """
        Toggle the door state between open and closed.
        """

        self.opened = not self.opened
        
        if self.opened:
            self._image = self._txt_open
        else:
            self._image = self._txt_closed

    def move_by_distance(self, distance: tuple[int, int]) -> None:
        """
        Move the door by a given distance.
        """

        self.rect.move_ip(distance)