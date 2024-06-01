from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import pygame as pg
from random import randint

if TYPE_CHECKING:
    from modules.spaceship.room import Room

from modules.resources import get_font

class Projectile():
    # public
    type: Literal["laser", "missile", "beam"]
    damage: int
    speed: float
    color: tuple[int,int,int]
    length: int
    width: int
    delay: float
    hit_target: bool
    switched_screens: bool # determines if the projectile is on the enemy screen
    target_pos: tuple[int,int]
    future_pos: tuple[int,int]
    missed: bool
    enemy_projectile: bool

    # private
    _target_room: Room
    _vector2d_start: pg.math.Vector2
    _vector2d_end: pg.math.Vector2
    _font = get_font("arial", 20)
    _missed_label = _font.render("MISS", True, (255,0,0))
    _missed_pos = tuple[int, int]

    def __init__(self, 
                 start_pos: tuple[int,int],
                 first_pos: tuple[int, int],
                 type: Literal["laser", "missile", "beam"], 
                 damage: int = 1, 
                 speed: float = 5,
                 color: tuple[int,int,int] = (255,0,0),
                 length: int = 5,
                 width: int = 1,
                 delay: float = 0,
                 target_room: Room = None,
                 enemy_projectile: bool = False
                 ):
        self.type = type
        self.damage = damage
        self.speed = speed
        self.color = color
        self.length = length
        self.width = width
        self.delay = delay
        self._target_room = target_room
        self.hit_target = False
        self.missed = False
        self.enemy_projectile = enemy_projectile

        self.switched_screens = False
        
        self.target_pos = first_pos
        self.future_pos = (
            self._target_room.rect.centerx + randint(-self._target_room.rect.width // 2, self._target_room.rect.width // 2),
            self._target_room.rect.centery + randint(-self._target_room.rect.height // 2, self._target_room.rect.height // 2)
        )
        self._vector2d_start = pg.math.Vector2(start_pos)
        self._vector2d_end = self._vector2d_start.move_towards(self.target_pos, length)
    
    def update(self, dt: float) -> None:
        """
        Update the projectile's position and draw it on the screen.
        :param dt: float - the time since the last frame
        """
        if self.delay <= 0:
            self._vector2d_start.move_towards_ip(self.target_pos, self.speed * dt)
            self._vector2d_end.move_towards_ip(self.target_pos, self.speed * dt)
        else:
            self.delay -= dt
        
        # check if the projectile hit the shield
        shield = self._target_room.parent.installed_shield 
        if shield is not None and self.switched_screens:
            if hasattr(shield, "shield_mask") and shield.charge > 0:
                # TODO: Sometimes the normalized pos is in the negatives (outside of shield.mask.get_size() range)
                normalized_pos = (self._vector2d_end[0] - shield.pos[0], self._vector2d_end[1] - shield.pos[1])
                shield_mask_size = shield.shield_mask.get_size()
                if normalized_pos[0] < 0 or normalized_pos[1] < 0:
                    pass
                elif normalized_pos[0] <= shield_mask_size[0] and normalized_pos[1] <= shield_mask_size[1] and shield.shield_mask.get_at(normalized_pos) == 1:
                    self.hit_target = True
                    shield.take_damage(self)
        del shield

        # check if the projectile hit the target room
        if self._vector2d_start == self.target_pos:
            if not self.missed:
                if randint(0,100) < self._target_room.parent.evade_stat:
                    self._missed_pos = self.target_pos
                    self.target_pos = (-self.target_pos[1], self.target_pos[0]*2)
                    self._vector2d_start.move_towards_ip(self.target_pos, self.length)
                    self.missed = True
                else:
                    self._target_room.take_damage(self)
                    self.hit_target = True
            else:
                self.hit_target = True

        if self.missed:
            if not self.enemy_projectile:
                self._missed_pos = (self._missed_pos[0] + 0.5, self._missed_pos[1])
            else:
                self._missed_pos = (self._missed_pos[0], self._missed_pos[1] - 0.5)

    def draw(self, screen: pg.surface.Surface) -> None:
        """
        Draw the projectile on the screen.
        :param screen: pg.surface.Surface - the screen to draw the projectile on
        """
        if self.delay <= 0:
            pg.draw.line(screen, self.color, self._vector2d_start, self._vector2d_end, self.width)
        
        if self.missed:
            if not self.enemy_projectile:
                screen.blit(pg.transform.rotate(self._missed_label, 270), self._missed_pos)
            else:
                screen.blit(self._missed_label, self._missed_pos)

    def update_vectors(self, new_pos: tuple[int, int]) -> None:
        """
        Update the projectile's position and target.
        :param new_pos: tuple[int, int] - the new position of the projectile
        :param new_target: tuple[int, int] - the new target of the projectile
        """
        self.target_pos = self.future_pos
        self._vector2d_start = pg.math.Vector2(new_pos)
        self._vector2d_end = self._vector2d_start.move_towards(self.target_pos, self.length)

    def position(self) -> tuple[float, float, int]:
        """
        Returns the projectile's position and length.
        :return: tuple[float, float, int] - the projectile's start x, y and length
        """

        return self._vector2d_start.x, self._vector2d_start.y, self.length
    
    def __del__(self) -> None:
        """Delete the projectile."""
        del self