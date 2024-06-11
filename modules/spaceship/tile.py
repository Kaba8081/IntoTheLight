import pygame as pg
from modules.resources import textures

class Tile(pg.sprite.Sprite):
    # public
    pos: tuple[int,int]
    rect: pg.Rect
    hitbox: pg.Rect
    image: pg.Surface

    # private
    _occupied: bool
    _selected: bool

    def __init__(self, 
                 parent_pos: tuple, 
                 pos: tuple, 
                 sprite_group: pg.sprite.Group
                 ) -> None:
        pg.sprite.Sprite.__init__(self, sprite_group)
        
        self.image = textures["tile_default"].copy()
        self.rect = self.image.get_rect()

        self.pos = pos
        self.rect.x = parent_pos[0] + pos[0] * 32
        self.rect.y = parent_pos[1] + pos[1] * 32

        self.hitbox = self.rect.copy()

        self._occupied = False
        self._selected = False
    
    @property
    def occupied(self) -> bool:
        """Returns True or False depending on if the tile is occupied by a crewmate."""
        return self._occupied
    
    @occupied.setter
    def occupied(self, value: bool) -> None:
        """Sets the tile's occupied status."""

        self._occupied = value
        
        # if occupied set to true, set selected to false
        if value:
            self.selected = False

    @property
    def selected(self) -> bool:
        """Returns True or False depending on if the tile is selected."""
        return self._selected
    
    @selected.setter
    def selected(self, value: bool) -> None:
        """Sets the tile's selected status."""

        if value and self._selected!= value: # apply the selected texture only once
            self.image.blit(textures["crewmates"]["destination"].image, (0,0))
        elif not value:
            self.image = textures["tile_default"].copy()
        
        self._selected = value