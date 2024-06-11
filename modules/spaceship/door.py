import pygame as pg

from modules.resources import textures

class Door(pg.sprite.Sprite):
    # public
    rect: pg.Rect
    hitbox: pg.Rect

    image: pg.Surface

    opened: bool
    opened_cooldown: int = 60 # time the door stays open
    opened_timer: int = 0 # time the door has been open

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

        self.hitbox = self.rect.copy()

        self.opened = False

    def toggle(self) -> None:
        """
        Toggle the door state between open and closed.
        """

        if self.opened_timer == 0: # toggle the door only if it's not already open
            self.opened = not self.opened
            
            if self.opened:
                self.image = self._txt_open
            else:
                self.image = self._txt_closed
    
    def update(self) -> None:
        """
        Update the door state.
        """

        if self.opened:
            self.opened_timer += 1
            if self.opened_timer >= self.opened_cooldown:
                self.opened = False
                self.opened_timer = 0
                self.image = self._txt_closed
        else:
            self.image = self._txt_closed